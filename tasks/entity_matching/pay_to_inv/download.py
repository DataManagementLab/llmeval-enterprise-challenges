import collections
import datetime
import functools
import json
import logging
import os
import random

import attrs
import hydra
import numpy as np
import pandas as pd
import tqdm
from faker import Faker
from omegaconf import DictConfig

from llms4de.data import get_download_dir, dump_cfg
from llms4de.fake import unique
from llms4de.prompting.template import fill_template

pd.options.mode.chained_assignment = None  # default='warn'

logger = logging.getLogger(__name__)

random = random.Random(282583054)
np_random = np.random.RandomState(657579608)
faker = Faker()
faker.seed_instance(296105382)


class Match(dict):
    pass


class Invoice(dict):
    pass


class Payment(dict):
    pass


@attrs.define
class Context:
    matches: list[Match]
    invoices: list[Invoice]
    payments: list[Payment]

    @classmethod
    def empty(cls) -> "Context":
        return cls([], [], [])


class Registry(list):
    def register(self, generator):
        self.append(generator)
        return generator


class NamedRegistry(dict):
    def register(self, attrib):
        def f(generator):
            self[attrib] = generator
            return generator

        return f


def random_sap_number(n_digits: int) -> str:
    betavariate = random.betavariate(1, 10 ** (n_digits - 5))
    return str(10 ** (n_digits - 1) + int(betavariate * (10 ** (n_digits - 1) - 1)))


def round_currency(amount: float) -> float:
    return round(amount, 2)


def exponential_drop(l: list | range, denom: int) -> int:
    v = list(l)
    w = [1 / denom ** i for i in range(len(v))]
    return random.choices(v, weights=w)[0]


########################################################################################################################
# match generation
########################################################################################################################


def sample_match_category(cfg: DictConfig) -> str:
    return random.choices(
        list(cfg.dataset.match_categories.keys()),
        weights=[mc.weight for mc in cfg.dataset.match_categories.values()]
    )[0]


def sample_perturbation_categories(cfg: DictConfig) -> list[str]:
    if random.random() > cfg.dataset.perturbation_probability:
        return []

    perturbation_categories = list(cfg.dataset.perturbation_categories.keys())
    weights = [c.weight for c in cfg.dataset.perturbation_categories.values()]
    weights = [w / sum(weights) for w in weights]

    match cfg.dataset.perturbation_mode:
        case "single":
            return random.choices(perturbation_categories, weights=weights)
        case "multi":
            num_perturbations = random.randint(1, len(cfg.dataset.perturbation_categories))
            return list(np_random.choice(perturbation_categories, p=weights, replace=False, size=num_perturbations))
        case _:
            raise AssertionError(f"invalid perturbation_mode `{cfg.dataset.perturbation_mode}`")


def generate_match(context: Context, cfg: DictConfig) -> Match:
    match = Match(match_id=len(context.matches))

    match["match_category"] = sample_match_category(cfg)
    match["perturbation_categories"] = sample_perturbation_categories(cfg)

    match_fillers[match["match_category"]](match, context, cfg)

    context.matches.append(match)
    return match


match_fillers = NamedRegistry()


@match_fillers.register("one_pay_one_inv")
def generate_one_pay_one_inv_match(match: Match, context: Context, cfg: DictConfig) -> None:
    invoice = generate_invoice(match, context, cfg)

    match["match_info"] = {
        "inv_billing_number": invoice["inv_billing_number"],
        "inv_assignment_number": invoice["inv_assignment_number"],
        "inv_amount": invoice["inv_amount"],
        "inv_currency_code": invoice["inv_currency_code"],
        "inv_customer_id": invoice["inv_customer_id"],
        "inv_customer_name": invoice["inv_customer_name"],
        "inv_company_code": invoice["inv_company_code"],
        "inv_country_key": invoice["inv_country_key"],
        "inv_document_date": invoice["inv_document_date"]
    }

    payment = generate_payment(match, context, cfg)

    match["invoice_ids"] = [invoice["invoice_id"]]
    match["payment_ids"] = [payment["payment_id"]]


@match_fillers.register("multi_pay_one_inv")
def generate_multi_pay_one_inv_match(match: Match, context: Context, cfg: DictConfig) -> None:
    gen_cfg = cfg.dataset.match_categories[match["match_category"]].gen
    invoice = generate_invoice(match, context, cfg)

    betavariate = random.betavariate(gen_cfg.num_payments_alpha, gen_cfg.num_payments_beta)
    num_payments = 2 + int(betavariate * (gen_cfg.max_num_payments - 2))

    pay_amounts = [random.random() for _ in range(num_payments)]
    pay_amounts = [amount / sum(pay_amounts) * invoice["inv_amount"] for amount in pay_amounts]
    pay_amounts = [round_currency(amount) for amount in pay_amounts]
    pay_amounts[-1] = sum(pay_amounts) - sum(pay_amounts[:-1])

    match["match_info"] = {
        "inv_billing_number": invoice["inv_billing_number"],
        "inv_assignment_number": invoice["inv_assignment_number"],
        "inv_currency_code": invoice["inv_currency_code"],
        "inv_customer_id": invoice["inv_customer_id"],
        "inv_customer_name": invoice["inv_customer_name"],
        "inv_country_key": invoice["inv_country_key"],
        "inv_company_code": invoice["inv_company_code"],
        "inv_document_date": invoice["inv_document_date"],
        "pay_amounts": pay_amounts
    }

    payments = []
    for pay_counter in range(len(pay_amounts)):
        match["match_info"]["pay_counter"] = pay_counter
        payments.append(generate_payment(match, context, cfg))

    match["invoice_ids"] = [invoice["invoice_id"]]
    match["payment_ids"] = [payment["payment_id"] for payment in payments]


@match_fillers.register("one_pay_multi_inv")
def generate_one_pay_multi_inv_match(match: Match, context: Context, cfg: DictConfig) -> None:
    gen_cfg = cfg.dataset.match_categories[match["match_category"]].gen

    betavariate = random.betavariate(gen_cfg.num_invoices_alpha, gen_cfg.num_invoices_beta)
    num_invoices = 2 + int(betavariate * (gen_cfg.max_num_invoices - 2))

    # generate the first invoice as one_pay_one_inv
    match["match_category"] = "one_pay_one_inv"
    invoice = generate_invoice(match, context, cfg)

    # generate remaining invoices as one_pay_multi_inv
    match["match_category"] = "one_pay_multi_inv"
    match["match_info"] = {
        "inv_customer_id": invoice["inv_customer_id"],
        "inv_fiscal_year": invoice["inv_fiscal_year"],
        "inv_company_code": invoice["inv_company_code"],
    }
    invoices = [invoice]
    for _ in range(num_invoices - 1):
        invoices.append(generate_invoice(match, context, cfg))

    match["match_info"]["all_inv_billing_numbers"] = [inv["inv_billing_number"] for inv in invoices]
    match["match_info"]["all_inv_assignment_numbers"] = [inv["inv_assignment_number"] for inv in invoices]
    match["match_info"]["inv_currency_code"] = invoices[0]["inv_currency_code"]
    match["match_info"]["inv_customer_name"] = invoices[0]["inv_customer_name"]
    match["match_info"]["inv_customer_id"] = invoices[0]["inv_customer_id"]
    match["match_info"]["inv_country_key"] = invoices[0]["inv_country_key"]
    match["match_info"]["inv_company_code"] = invoices[0]["inv_company_code"]
    match["match_info"]["total_inv_amount"] = sum(inv["inv_amount"] for inv in invoices)
    match["match_info"]["all_inv_document_dates"] = [inv["inv_document_date"] for inv in invoices]

    payment = generate_payment(match, context, cfg)

    match["invoice_ids"] = [invoice["invoice_id"] for invoice in invoices]
    match["payment_ids"] = [payment["payment_id"]]


########################################################################################################################
# invoice generation
########################################################################################################################


def generate_invoice(match: Match, context: Context, cfg: DictConfig) -> Invoice:
    invoice = Invoice(invoice_id=len(context.invoices))
    for attr_filler in inv_attr_fillers:
        attr_filler(invoice, match, context, cfg)
    context.invoices.append(invoice)
    return invoice


inv_attr_fillers = Registry()


@inv_attr_fillers.register
def fill_inv_client(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CHAR3
    invoice["inv_client"] = "001"


@inv_attr_fillers.register
def fill_inv_company_code(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CHAR4
    match match["match_category"]:
        case "one_pay_multi_inv":
            invoice["inv_company_code"] = match["match_info"]["inv_company_code"]
        case _:
            # not-unique random string from ["1000", ..., "9000"], skewed towards lower values
            values = [f"{i}000" for i in range(1, 10)]
            gen_cfg = cfg.dataset.inv_attributes.inv_company_code.gen
            invoice["inv_company_code"] = exponential_drop(values, gen_cfg.value_exp_drop_denom)


@inv_attr_fillers.register
def fill_inv_fiscal_year(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # NUMC
    match match["match_category"]:
        case "one_pay_multi_inv":
            invoice["inv_fiscal_year"] = match["match_info"]["inv_fiscal_year"]
        case _:
            # not-unique random year (integer) between min_year and max_year
            invoice["inv_fiscal_year"] = random.randint(
                cfg.dataset.inv_attributes.inv_fiscal_year.gen.min_year,
                cfg.dataset.inv_attributes.inv_fiscal_year.gen.max_year
            )


@inv_attr_fillers.register
def fill_inv_document_number(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CHAR10
    # unique random 10-digit integer string with leading 1, skewed towards lower values
    document_number = unique(lambda: random_sap_number(10), [inv["inv_document_number"] for inv in context.invoices])
    invoice["inv_document_number"] = document_number


@inv_attr_fillers.register
def fill_inv_line_item_number(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CHAR3
    # not-unique random string from ["001", ..., "009"], skewed towards lower values
    values = [f"00{i}" for i in range(1, 10)]
    gen_cfg = cfg.dataset.inv_attributes.inv_line_item_number.gen
    invoice["inv_line_item_number"] = exponential_drop(values, gen_cfg.value_exp_drop_denom)


@inv_attr_fillers.register
def fill_inv_assignment_number(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CHAR18
    # unique "INV" + random 15-digit integer string with leading 1, skewed towards lower values
    invoice["inv_assignment_number"] = unique(
        lambda: f"INV{random_sap_number(15)}",
        [inv["inv_assignment_number"] for inv in context.invoices]
    )


@inv_attr_fillers.register
def fill_inv_billing_number(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CHAR10
    # unique random 10-digit integer string or last 10 digits of assignment number
    gen_cfg = cfg.dataset.inv_attributes.inv_billing_number.gen

    def generator() -> str:
        if random.random() < gen_cfg.not_from_assignment_number:
            return str(random.randint(0, 9999999999)).zfill(10)
        else:
            return invoice["inv_assignment_number"][:-10]

    invoice["inv_billing_number"] = unique(
        generator,
        [inv["inv_billing_number"] for inv in context.invoices]
    )


def random_inv_customer_id() -> str:
    customer_id = "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(3))
    customer_id += "".join(random.choice("0123456789") for _ in range(7))
    return customer_id


@functools.cache
def random_inv_customer_ids(num_customers: int) -> list[str]:
    customer_ids = []
    for _ in range(num_customers):
        customer_ids.append(unique(random_inv_customer_id, customer_ids))
    return customer_ids


@inv_attr_fillers.register
def fill_inv_customer_id(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CHAR10
    match match["match_category"]:
        case "one_pay_multi_inv":
            invoice["inv_customer_id"] = match["match_info"]["inv_customer_id"]
        case _:
            # not-unique random string with schema "ABC01234567" sampled from population of size num_customers
            random_customer_ids = random_inv_customer_ids(cfg.dataset.inv_attributes.inv_customer_id.gen.num_customers)
            invoice["inv_customer_id"] = random.choice(random_customer_ids)


fixed_customer_names = {}


@inv_attr_fillers.register
def fill_inv_customer_name(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CHAR35
    # unique random company name, fixed for each inv_customer_id
    if invoice["inv_customer_id"] not in fixed_customer_names.keys():
        gen_cfg = cfg.dataset.inv_attributes.inv_customer_name.gen
        match gen_cfg.mode:
            case "faker":
                generator = lambda: faker.company()[:35]
            case "chatgpt":
                prev_names = set(inv["inv_customer_name"] for inv in context.invoices)
                chatgpt_companies = [v["name"][:35] for v in gen_cfg.chatgpt_companies if
                                     v["name"][:35] not in prev_names]
                generator = lambda: random.choice(chatgpt_companies)
            case _:
                raise AssertionError(f"invalid inv_customer_name generation mode `{gen_cfg.mode}`")

        inv_customer_name = unique(generator, [inv["inv_customer_name"] for inv in context.invoices])
        fixed_customer_names[invoice["inv_customer_id"]] = inv_customer_name

    invoice["inv_customer_name"] = fixed_customer_names[invoice["inv_customer_id"]]


fixed_currency_codes = {}


@inv_attr_fillers.register
def fill_inv_currency_code(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CUKY5
    # not-unique random (weighted) currency code, fixed for each inv_customer_id
    if invoice["inv_customer_id"] not in fixed_currency_codes.keys():
        gen_cfg = cfg.dataset.inv_attributes.inv_currency_code.gen
        currency_codes = list(gen_cfg.currency_codes.keys())
        weights = list(gen_cfg.currency_codes.values())
        inv_currency_code = random.choices(currency_codes, weights)[0]
        fixed_currency_codes[invoice["inv_customer_id"]] = inv_currency_code

    invoice["inv_currency_code"] = fixed_currency_codes[invoice["inv_customer_id"]]


fixed_country_key_and_country_name = {}


@inv_attr_fillers.register
def fill_inv_country_key_and_country_name(invoice: Invoice, match: Match, context: Context,
                                          cfg: DictConfig) -> None:  # CHAR35
    # unique random country key and country name, fixed for each inv_customer_id
    if invoice["inv_customer_id"] not in fixed_country_key_and_country_name.keys():
        ci = random.choice(cfg.dataset.inv_attributes.inv_country_key.gen[invoice["inv_currency_code"]])
        fixed_country_key_and_country_name[invoice["inv_customer_id"]] = ci["country_code"], ci["country_name"]

    invoice["inv_country_key"], invoice["inv_country_name"] = fixed_country_key_and_country_name[
        invoice["inv_customer_id"]]


@inv_attr_fillers.register
def fill_inv_amount(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CURR13,2
    # random amount between 0 and max_amount USD, skewed towards lower values
    gen_cfg = cfg.dataset.inv_attributes.inv_amount.gen
    usd_amount = random.betavariate(gen_cfg.amount_alpha, gen_cfg.amount_beta) * gen_cfg.max_amount
    invoice["inv_amount"] = round_currency(usd_amount * gen_cfg.usd_to_currency[invoice["inv_currency_code"]])


@inv_attr_fillers.register
def fill_inv_document_date(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # DATS8
    # not-unique random date in the year of inv_fiscal_year
    date = faker.date("2024-09-20T00:00:00.000Z")
    if date[5:7] == "02" and date[8:10] == "29":  # take leap years into account
        date = date[:8] + "28"
    invoice["inv_document_date"] = str(invoice["inv_fiscal_year"]) + date[5:7] + date[8:10]


@inv_attr_fillers.register
def fill_inv_due_date(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # DATS8
    # not-unique random date up to max_days_since_document_date after inv_document_date, skewed towards lower values
    gen_cfg = cfg.dataset.inv_attributes.inv_due_date.gen
    days_since = int(random.betavariate(gen_cfg.days_since_alpha, gen_cfg.days_since_beta) * gen_cfg.max_days_since)
    document_date = datetime.datetime.strptime(invoice["inv_document_date"], "%Y%m%d")
    due_date = document_date + datetime.timedelta(days=days_since)
    invoice["inv_due_date"] = due_date.strftime("%Y%m%d")


fixed_terms_of_payment = {}


@inv_attr_fillers.register
def fill_inv_terms_of_payment(invoice: Invoice, match: Match, context: Context, cfg: DictConfig) -> None:  # CHAR4
    # not-unique random integer, fixed for each pair of (inv_customer_id, inv_company_code)
    invoice["inv_terms_of_payment"] = fixed_terms_of_payment.setdefault(
        (invoice["inv_customer_id"], invoice["inv_company_code"]),
        str(random.randint(1, cfg.dataset.inv_attributes.inv_terms_of_payment.gen.max_terms_of_payment)).zfill(4)
    )


########################################################################################################################
# payment generation
########################################################################################################################


def generate_payment(match: Match, context: Context, cfg: DictConfig) -> Payment:
    payment = Payment(payment_id=len(context.payments))
    for attr_filler in pay_attr_fillers:
        attr_filler(payment, match, context, cfg)
    context.payments.append(payment)
    return payment


pay_attr_fillers = Registry()


def break_name(s: str) -> str:
    if random.random() < 0.5:
        for suffix in ("Inc", "and Sons", "LLC", "Group", "PLC", "Ltd"):
            if s.endswith(suffix):
                s = s[:len(suffix)]
    if random.random() < 0.25:
        s = s.lower()
    elif random.random() < 0.5:
        s = s.upper()
    return s


@pay_attr_fillers.register
def fill_pay_business_partner(payment: Payment, match: Match, context: Context, cfg: DictConfig) -> None:
    if "perturbed_business_partner" in match["perturbation_categories"]:
        gen_cfg = cfg.dataset.inv_attributes.inv_customer_name.gen
        match gen_cfg.mode:
            case "chatgpt":
                for d in gen_cfg.chatgpt_companies:
                    if d["name"] == match["match_info"]["inv_customer_name"]:
                        payment["pay_business_partner"] = d["bank_statement"]
                        break
                else:
                    raise AssertionError(
                        f"no bank statement name for inv_customer_name `{match['match_info']['inv_customer_name']}`")
            case "faker":
                payment["pay_business_partner"] = break_name(match["match_info"]["inv_customer_name"])
            case _:
                raise AssertionError("Invalid inv_customer_name generation mode!")
    else:
        payment["pay_business_partner"] = match["match_info"]["inv_customer_name"]


fixed_account_numbers = {}


@pay_attr_fillers.register
def fill_pay_account_number(payment: Payment, match: Match, context: Context, cfg: DictConfig) -> None:
    def make_iban():
        return match["match_info"]["inv_country_key"] + faker.iban()[2:]

    payment["pay_account_number"] = fixed_account_numbers.setdefault(
        (match["match_info"]["inv_customer_id"], match["match_info"]["inv_company_code"]),
        unique(make_iban, [pay["pay_account_number"] for pay in context.payments])
    )


def break_identifier(s: str) -> str:
    c = random.random()
    if c < 0.2:
        if len(s) < 2:
            return s
        # add a space
        i = random.randint(1, len(s) - 1)
        return s[:i] + " " + s[i:]
    elif c <= 0.4:
        if len(s) < 5:
            return s
        # remove a digit
        i = random.randint(0, len(s) - 1)
        return s[:i] + s[i + 1:]
    elif c <= 0.6:
        # add a new digit
        i = random.randint(0, len(s))
        new_digit = random.choice("0123456789")
        return s[:i] + new_digit + s[i:]
    elif c <= 0.8:
        if len(s) < 2:
            return s
        # swap two digits
        i = random.randint(0, len(s) - 2)
        return s[:i] + s[i + 1] + s[i] + s[i + 2:]
    else:
        if len(s) < 5:
            return s
        # cut digits at start or end
        j = exponential_drop(range(1, len(s)), 4)
        if random.random() < 0.5:
            return s[:-j]
        else:
            return s[j:]


def generate_memo_line_template() -> str:
    t = random.choice(["#RECEIPT: ", "payment ", "ORDER OF ", "PAY ", "RECEIPT ", "receipt number ", ""])
    if random.random() < 0.5:
        t += "{{billing_number}} "
        if random.random() < 0.2:
            t += "{{noisy_id_1}} "
        t += "{{assignment_number}}"
    else:
        t += "{{assignment_number}} "
        if random.random() < 0.2:
            t += "{{noisy_id_1}} "
        t += "{{billing_number}}"

    if random.random() < 0.2:
        if random.random() < 0.5:
            t += random.choice([" REF", " ref", " REFERENCE", " NUM", " NO"])
        t += " {{noisy_id_2}}"
    return t


fixed_memo_line_templates = {}


def generate_memo_line_multi_inv_parts() -> tuple[str, str]:
    prefix = random.choice(["REF {{idx}}: ", "ref {{idx}}: ", "no {{idx}}: ", "NO {{idx}}: ", "+ ", "- ", ""])
    sep = random.choice(["", " ", ", ", " & ", " | "])
    return prefix + "{{identifier}}", sep


fixed_memo_line_multi_inv_parts = {}


@pay_attr_fillers.register
def fill_pay_memo_line(payment: Payment, match: Match, context: Context, cfg: DictConfig) -> None:
    template = fixed_memo_line_templates.setdefault(
        match["match_info"]["inv_customer_id"],
        generate_memo_line_template()
    )
    multi_inv_template, sep = fixed_memo_line_multi_inv_parts.setdefault(
        match["match_info"]["inv_customer_id"],
        generate_memo_line_multi_inv_parts()
    )
    noisy_id_1 = str(random_sap_number(random.randint(3, 15)))
    noisy_id_2 = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(random.randint(3, 15)))
    match match["match_category"]:
        case "one_pay_multi_inv":
            billing_numbers = match["match_info"]["all_inv_billing_numbers"]
            if "perturbed_billing_number" in match["perturbation_categories"]:
                billing_numbers = [break_identifier(billing_number) for billing_number in billing_numbers]
            billing_number = sep.join(
                [fill_template(multi_inv_template, idx=str(idx), identifier=billing_number) for idx, billing_number in
                 enumerate(billing_numbers)])
            payment["pay_memo_line"] = fill_template(
                template,
                billing_number=billing_number,
                assignment_number="",
                noisy_id_1=noisy_id_1,
                noisy_id_2=noisy_id_2
            )
        case _:
            clean_billing_number = str(match["match_info"]["inv_billing_number"])
            if "perturbed_billing_number" in match["perturbation_categories"]:
                billing_number = break_identifier(clean_billing_number)
            else:
                if random.random() < 0.2:
                    billing_number = clean_billing_number
                else:
                    billing_number = ""
            clean_assignment_number = str(match["match_info"]["inv_assignment_number"])
            if "perturbed_assignment_number" in match["perturbation_categories"]:
                assignment_number = break_identifier(clean_assignment_number)
            else:
                if random.random() < 0.2:
                    assignment_number = clean_assignment_number
                else:
                    assignment_number = ""

            if billing_number == "" and assignment_number == "":
                if random.random() < 0.5:
                    billing_number = clean_billing_number
                else:
                    assignment_number = clean_assignment_number

            payment["pay_memo_line"] = fill_template(
                template,
                billing_number=billing_number,
                assignment_number=assignment_number,
                noisy_id_1=noisy_id_1,
                noisy_id_2=noisy_id_2
            )


@pay_attr_fillers.register
def fill_pay_amount(payment: Payment, match: Match, context: Context, cfg: DictConfig) -> None:
    match match["match_category"]:
        case "multi_pay_one_inv":
            amount = match["match_info"]["pay_amounts"][match["match_info"]["pay_counter"]]
        case "one_pay_multi_inv":
            amount = match["match_info"]["total_inv_amount"]
        case _:
            amount = match["match_info"]["inv_amount"]

    if "small_deduction" in match["perturbation_categories"]:
        gen_cfg = cfg.dataset.perturbation_categories.small_deduction.gen
        inv_amount_gen_cfg = cfg.dataset.inv_attributes.inv_amount.gen
        deduction_usd = random.betavariate(gen_cfg.deduction_alpha, gen_cfg.deduction_beta) * gen_cfg.max_deduction_usd
        usd_to_currency = inv_amount_gen_cfg.usd_to_currency[match["match_info"]["inv_currency_code"]]
        deduction = round_currency(min(amount * gen_cfg.max_deduction_frac, deduction_usd * usd_to_currency))
        amount -= deduction

    payment["pay_amount"] = str(amount)


@pay_attr_fillers.register
def fill_pay_currency(payment: Payment, match: Match, context: Context, cfg: DictConfig) -> None:
    payment["pay_currency"] = match["match_info"]["inv_currency_code"]


@pay_attr_fillers.register
def fill_pay_posting_date(payment: Payment, match: Match, context: Context, cfg: DictConfig) -> None:
    # not-unique random date up to max_days_since_document_date after the final inv_document_date, skewed towards lower values
    gen_cfg = cfg.dataset.pay_attributes.pay_posting_date.gen
    days_since = int(random.betavariate(gen_cfg.days_since_alpha, gen_cfg.days_since_beta) * gen_cfg.max_days_since)

    match match["match_category"]:
        case "one_pay_multi_inv":
            document_date = list(sorted(match["match_info"]["all_inv_document_dates"]))[-1]
        case _:
            document_date = match["match_info"]["inv_document_date"]

    document_date = datetime.datetime.strptime(document_date, "%Y%m%d")
    posting_date = document_date + datetime.timedelta(days=days_since)
    payment["pay_posting_date"] = posting_date.strftime("%Y%m%d")


########################################################################################################################
# main
########################################################################################################################


@hydra.main(version_base=None, config_path="../../../config/entity_matching", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "pay_to_inv", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name, clear=True)

    for perturbation_mode in ["single", "multi"]:
        logger.info(f"Generating for perturbation_mode `{perturbation_mode}`.")
        cfg.dataset.perturbation_mode = perturbation_mode
        os.makedirs(download_dir / perturbation_mode)

        context = Context.empty()

        logger.info("Generate matches.")
        for _ in tqdm.trange(cfg.dataset.num_matches, desc="generate matches"):
            generate_match(context, cfg)

        logger.info("Turn context into dataframes.")
        invoices = pd.DataFrame(context.invoices)
        payments = pd.DataFrame(context.payments)
        matches = pd.DataFrame(context.matches)
        matches["perturbation_categories"] = matches["perturbation_categories"].apply(json.dumps)
        matches["invoice_ids"] = matches["invoice_ids"].apply(json.dumps)
        matches["payment_ids"] = matches["payment_ids"].apply(json.dumps)
        matches = matches[["match_id", "match_category", "perturbation_categories", "invoice_ids", "payment_ids"]]

        logger.info("Create descriptive version of the dataset.")
        os.makedirs(download_dir / perturbation_mode / "descriptive")
        invoices_d = invoices[
            ["invoice_id"] + [n for n, c in cfg.dataset.inv_attributes.items() if c.single_table.include_in_view]
            ]
        m = {n: c.descriptive_name for n, c in cfg.dataset.inv_attributes.items() if c.single_table.include_in_view}
        invoices_d = invoices_d.rename(columns=m)
        invoices_d.to_csv(download_dir / perturbation_mode / "descriptive" / "invoices.csv", index=False)

        payments_d = payments[
            ["payment_id"] + [n for n, c in cfg.dataset.pay_attributes.items() if c.single_table.include_in_view]
            ]
        m = {n: c.descriptive_name for n, c in cfg.dataset.pay_attributes.items() if c.single_table.include_in_view}
        payments_d = payments_d.rename(columns=m)
        payments_d.to_csv(download_dir / perturbation_mode / "descriptive" / "payments.csv", index=False)

        matches.to_csv(download_dir / perturbation_mode / "descriptive" / "matches.csv", index=False)

        logger.info("Create opaque version of the dataset.")
        os.makedirs(download_dir / perturbation_mode / "opaque")
        invoices_o = invoices[
            ["invoice_id"] + [a for a, c in cfg.dataset.inv_attributes.items() if c.single_table.include_in_view]
            ]
        m = {n: c.opaque_name for n, c in cfg.dataset.inv_attributes.items() if c.single_table.include_in_view}
        invoices_o = invoices_o.rename(columns=m)
        invoices_o.to_csv(download_dir / perturbation_mode / "opaque" / "invoices.csv", index=False)

        payments_o = payments[
            ["payment_id"] + [n for n, c in cfg.dataset.pay_attributes.items() if c.single_table.include_in_view]
            ]
        m = {a: c.opaque_name for a, c in cfg.dataset.pay_attributes.items() if c.single_table.include_in_view}
        payments_o = payments_o.rename(columns=m)
        payments_o.to_csv(download_dir / perturbation_mode / "opaque" / "payments.csv", index=False)

        matches.to_csv(download_dir / perturbation_mode / "opaque" / "matches.csv", index=False)

        logger.info("Create multi-table version of the dataset.")
        os.makedirs(download_dir / perturbation_mode / "multi-table")

        inv_tables = collections.defaultdict(lambda: pd.DataFrame({"invoice_id": invoices["invoice_id"]}))
        inv_tables_primary_keys = collections.defaultdict(set)
        for attr_name, attr_config in cfg.dataset.inv_attributes.items():
            for table_name in attr_config.multi_table.table_names:
                inv_tables[table_name][attr_config.opaque_name] = invoices[attr_name]
            for table_name in attr_config.multi_table.is_primary_key_for:
                inv_tables_primary_keys[table_name].add(attr_config.opaque_name)

        for table_name, table in inv_tables.items():
            invoice_ids = collections.defaultdict(list)  # maps primary keys to list of invoice ids
            for _, row in table.iterrows():
                invoice_ids[tuple(row[list(inv_tables_primary_keys[table_name])].to_list())].append(row["invoice_id"])
            table.drop_duplicates(subset=list(inv_tables_primary_keys[table_name]), inplace=True)
            table["invoice_id"] = [invoice_ids[tuple(row[list(inv_tables_primary_keys[table_name])])] for _, row in
                                   table.iterrows()]
            table.reset_index(drop=True, inplace=True)
            table.to_csv(download_dir / perturbation_mode / "multi-table" / f"invoices_{table_name}.csv", index=False)

        pay_tables = collections.defaultdict(lambda: pd.DataFrame({"payment_id": payments["payment_id"]}))
        pay_tables_primary_keys = collections.defaultdict(set)
        for attr_name, attr_config in cfg.dataset.pay_attributes.items():
            for table_name in attr_config.multi_table.table_names:
                pay_tables[table_name][attr_config.opaque_name] = payments[attr_name]
            for table_name in attr_config.multi_table.is_primary_key_for:
                pay_tables_primary_keys[table_name].add(attr_config.opaque_name)

        for table_name, table in pay_tables.items():
            payment_ids = collections.defaultdict(list)  # maps primary keys to list of payment ids
            for _, row in table.iterrows():
                payment_ids[tuple(row[list(pay_tables_primary_keys[table_name])].to_list())].append(row["payment_id"])
            table.drop_duplicates(subset=list(pay_tables_primary_keys[table_name]), inplace=True)
            table["payment_id"] = [payment_ids[tuple(row[list(pay_tables_primary_keys[table_name])])] for _, row in
                                   table.iterrows()]
            table.reset_index(drop=True, inplace=True)
            table.to_csv(download_dir / perturbation_mode / "multi-table" / f"payments_{table_name}.csv", index=False)

        matches.to_csv(download_dir / perturbation_mode / "multi-table" / "matches.csv", index=False)

    dump_cfg(cfg, download_dir / "config.cfg")


if __name__ == "__main__":
    main()
