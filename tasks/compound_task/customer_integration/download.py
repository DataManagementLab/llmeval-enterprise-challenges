import datetime
import json
import logging
import os
import random
import string

import attrs
import hydra
import numpy as np
import pandas as pd
from faker import Faker
from omegaconf import DictConfig

from llms4de.data import get_download_dir
from llms4de.fake import unique

#########################################
#  Rules for Altering & Merging:
# - the non-altered row is the ground truth! (apart from customer_ID and creation name)
# - for every overlap customer, the creation date is increased when something is altered
# - the ground truth is the earliest creation date (valuable to know when a customer was first encountered) -> altering only increases the creation date
# - the ground truth is the latest modification date (assumption: newest contact information is correct) -> altering only decreases the modification date
# - when name or mail address are altered, the date modification date is always decreased
# - KUNNR should be the one from A, if customer is new in A create a 10-digit random number starting with 9
# - ERNAM (creation name) is from A if customer was only in A, otherwise 'mergescript'
#
#########################################


#################################
# General utilities
#################################

logger = logging.getLogger(__name__)

random = random.Random(28253342)
np_random = np.random.RandomState(61775608)
faker_seed = 3677834
faker = Faker()
faker.seed_instance(faker_seed)


class Registry(list):
    def register(self, generator):
        self.append(generator)
        return generator


class Customer(dict):
    pass


@attrs.define
class Context:
    customers: list[Customer]

    companies: list[dict]

    # needs to be unique:
    mail_addresses: list[str]
    phone_numbers: dict
    tax_numbers: list[int]

    creation_user_names_A: list[str]
    creation_user_names_B: list[str]

    customer_ids_in_A: list[str]
    customer_ids_in_B: list[str]

    @classmethod
    def empty(cls) -> "Context":
        return cls([], [], [], {}, [], [], [], [], [])


def random_sap_number(n_digits: int) -> str:
    betavariate = random.betavariate(1, 10 ** (n_digits - 5))
    return str(10 ** (n_digits - 1) + int(betavariate * (10 ** (n_digits - 1) - 1)))


def create_new_customer_id(context_ids: list[str], limit_for_A: bool = False):
    is_unique = False
    while not is_unique:
        if not limit_for_A:
            customer_id = "".join(random.choice("0123456789") for _ in range(10))
        else:
            # Company A IDs start from 0 to 8, keep 9 free for after merging
            customer_id = str(random.randint(0, 8999999999))
        if not customer_id in context_ids:
            is_unique = True
    return customer_id


def create_random_phone_suffix():
    return random.randint(111111, 99999999)


def create_tax_number():
    # Randomly determine the total length of the tax number
    total_length = random.randint(8, 15)

    # just use at most one character for non-VAT tax number
    alphanumeric_part = ''.join(random.choices(string.ascii_uppercase, k=random.randint(0, 1)))

    # Remaining part digits
    remaining_length = total_length - len(alphanumeric_part)
    numeric_part = ''.join(random.choices(string.digits, k=remaining_length))

    # Combine the numeric and alphanumeric parts
    tax_number = alphanumeric_part + numeric_part

    # Optionally add dashes
    if random.choice([True, False, False]):
        # Split the tax number into random segments and join with dashes
        segments = []
        while tax_number:
            segment_length = random.randint(2, 5)
            segments.append(tax_number[:segment_length])
            tax_number = tax_number[segment_length:]
        tax_number = '-'.join(segments)

    return tax_number


#################################
# Generate the customers
#################################

def generate_customer(context: Context, cfg: DictConfig):
    """
    Start dataset generation by generating all customers
    """
    customer = Customer(info_internal_id=len(context.customers))
    for attr_filler in customer_attr_fillers:
        attr_filler(customer, context, cfg)
    context.customers.append(customer)
    return customer


customer_attr_fillers = Registry()


@customer_attr_fillers.register
def fill_customer_client(customer: Customer, context: Context, cfg: DictConfig) -> None:  # CHAR3
    """
    Client field (MANDT)
    """
    customer["attr_client"] = "001"


@customer_attr_fillers.register
def fill_customer_address(customer: Customer, context: Context, cfg: DictConfig):
    """
    Address information & mail
    """
    found_unique = False
    while not found_unique:
        chosen_locales_info = random.choice(cfg.dataset.customer_details.locales)
        local_faker = Faker(chosen_locales_info.locale)
        local_faker.seed_instance(faker_seed + len(context.customers))

        # unique random company name
        generator = lambda: random.choice(chosen_locales_info.companies)
        try:
            customer_info = unique(generator, prev_values=context.companies)
            found_unique = True
        except:
            continue
    context.companies.append(customer_info)

    customer["attr_name"] = customer_info.name

    customer["attr_city"] = local_faker.city()
    customer["attr_zipcode"] = local_faker.postcode()
    customer["attr_country_name"] = chosen_locales_info.country_name
    customer["attr_country"] = chosen_locales_info.country_code
    customer["attr_street"] = local_faker.street_address().replace("\n", " ")

    # needs to be unique!
    assert customer_info.mail not in context.mail_addresses
    customer["attr_email"] = customer_info.mail
    context.mail_addresses.append(customer_info.mail)

    # tax number needs to be unique! 
    try:
        # try if local faker has a vat_id function implemented
        is_unique = False
        while not is_unique:
            tax_number = local_faker.vat_id().replace(" ", "")
            if tax_number not in context.tax_numbers:
                is_unique = True
                customer["attr_tax_vat"] = tax_number
                customer["attr_tax_other"] = None
    except Exception as e:
        tax_number = unique(create_tax_number, prev_values=context.tax_numbers)
        customer["attr_tax_vat"] = None
        customer["attr_tax_other"] = tax_number
    context.tax_numbers.append(tax_number)


@customer_attr_fillers.register
def fill_customer_phone_number(customer: Customer, context: Context, cfg: DictConfig):
    """
    Phone number + language
    """
    for d in cfg.dataset.customer_details.locales:
        if d["country_name"] == customer["attr_country_name"]:
            phone_prefix = d["phone"]
            break
    else:
        raise AssertionError(f"No locales info for country {customer['attr_country_name']}")

    customer["phone_prefix"] = phone_prefix
    if not phone_prefix in context.phone_numbers.keys():
        context.phone_numbers[phone_prefix] = []

    customer["phone_suffix"] = unique(create_random_phone_suffix, prev_values=context.phone_numbers[phone_prefix])
    context.phone_numbers[phone_prefix].append(customer["phone_suffix"])

    customer["attr_language"] = d["language"]


@customer_attr_fillers.register
def fill_customer_id(customer: Customer, context: Context, cfg: DictConfig):
    """
    Customer ID - will be filled later
    """
    customer["attr_customerID"] = "<placeholder>"


@customer_attr_fillers.register
def fill_customer_creation_info(customer: Customer, context: Context, cfg: DictConfig):
    """
    Customer Creation Date & creation name
    """
    creation_date = faker.date_between(start_date=datetime.date.fromisoformat('2000-12-12'),
                                       end_date=datetime.date.fromisoformat('2024-12-12'))

    customer["attr_creation_date"] = creation_date

    # customer["attr_creation_name"] = "<placeholder>"

    # always set modification date, to leave it empty or set to creation date creates a lot of special cases when altering
    customer["attr_modification_date"] = faker.date_between(start_date=creation_date,
                                                            end_date=datetime.date.fromisoformat('2024-12-12'))


@customer_attr_fillers.register
def fill_customer_account_type(customer: Customer, context: Context, cfg: DictConfig):
    """
    Customer Account type (char 4)
    """
    customer["attr_account"] = random.choice(list(cfg.dataset.account_groups.keys()))


@customer_attr_fillers.register
def fill_customer_currency(customer: Customer, context: Context, cfg: DictConfig):
    """
    Currency
    """
    for d in cfg.dataset.customer_details.locales:
        if d["country_name"] == customer["attr_country_name"]:
            currency_key = d["currency"]
            break
    else:
        raise AssertionError(f"No locales info for country {customer['attr_country_name']}")

    customer["attr_currency"] = currency_key


@customer_attr_fillers.register
def fill_customer_tax_numbers(customer: Customer, context: Context, cfg: DictConfig):
    """
    Tax numbers (VAT or non-VAT)
    """
    for d in cfg.dataset.customer_details.locales:
        if d["country_name"] == customer["attr_country_name"]:
            currency_key = d["currency"]
            break
    else:
        raise AssertionError(f"No locales info for country {customer['attr_country_name']}")

    customer["attr_currency"] = currency_key


#######################################
# Altering
#######################################

def perform_customer_altering(customer: Customer, context: Context, cfg: DictConfig):
    altered_customer = customer.copy()
    altered_info = []

    # always set newer creation date
    # get a date between original creation and modification date
    altered_create_date = faker.date_between(start_date=customer["attr_creation_date"],
                                             end_date=customer["attr_modification_date"])
    altered_customer["attr_creation_date"] = altered_create_date
    altered_info.append("create_date_newer")

    # always set older modification date
    # get a date between new creation and orig modification date
    altered_mod_date = faker.date_between(start_date=altered_create_date, end_date=customer["attr_modification_date"])
    altered_customer["attr_modification_date"] = altered_mod_date
    altered_info.append("mod_date_earlier")

    # find locales details: 
    company_info = None
    for d in cfg.dataset.customer_details.locales:
        if d["country_name"] == customer["attr_country_name"]:
            locale = d["locale"]
            for company in d["companies"]:
                if company["name"] == customer["attr_name"]:
                    company_info = company

    # change name & mail to previous mail & name
    if random.random() < cfg.dataset.percentages.alter_attribute:
        altered_customer["attr_name"] = company_info["previous_name"]
        altered_customer["attr_email"] = company_info["previous_mail"]
        altered_info.append("name_and_mail")
    else:
        # change mail to mail variation
        if random.random() < cfg.dataset.percentages.alter_attribute:
            altered_customer["attr_email"] = company_info["mail_variation"]
            altered_info.append("mail")

    # drop TAX number
    if random.random() < cfg.dataset.percentages.alter_attribute:
        altered_customer["attr_tax_vat"] = None
        altered_customer["attr_tax_other"] = None

    #### change address
    if random.random() < cfg.dataset.percentages.alter_attribute:
        # create faker for the locale (with seed)
        local_faker = Faker(locale)
        local_faker.seed_instance(faker_seed + len(customer["attr_name"]))

        # create new address and set the details 
        altered_customer["attr_street"] = local_faker.street_address().replace("\n", " ")
        # customer has moved to a new city in 60% of the cases
        if random.random() < 0.6:
            altered_customer["attr_city"] = local_faker.city()
            altered_customer["attr_zipcode"] = local_faker.postcode()
        altered_info.append("address")

    #### change telephone number, still needs to be unique
    if random.random() < cfg.dataset.percentages.alter_attribute:
        altered_customer["phone_suffix"] = random.randint(111111, 99999999)
        prefix = customer["phone_prefix"]
        customer["phone_suffix"] = unique(create_random_phone_suffix, prev_values=context.phone_numbers[prefix])
        context.phone_numbers[prefix].append(customer["phone_suffix"])
        altered_info.append("phone")

    return altered_customer, altered_info


#######################################
# Create final table
#######################################

def generate_final_table(all_customers: list[Customer], customers_in_A: list[Customer], cfg: DictConfig):
    """
    Should be in Company A dataformat (SAP)
    should include all the customers only from A and those only from B in company A format
    from overlap should include the not-altered information
    
    """
    final_customers = []

    for c in all_customers:
        customer_in_A = None
        if c["info_internal_id"] in [x["info_internal_id"] for x in customers_in_A]:
            customer_in_A = [x for x in customers_in_A if x["info_internal_id"] == c["info_internal_id"]][0]
        final_customer = {}

        for (attr_name, config_values) in cfg.dataset.company_A_attributes.items():
            sap_fieldname = config_values["name"]
            if attr_name == "attr_customerID":
                if customer_in_A:
                    final_customer[sap_fieldname] = customer_in_A[sap_fieldname]
                else:
                    final_customer[sap_fieldname] = "xxx"
            elif attr_name == "attr_creation_name":
                if customer_in_A and customer_in_A["info_is_from"] == "A":
                    final_customer[sap_fieldname] = customer_in_A[sap_fieldname]
                else:
                    final_customer[sap_fieldname] = "mergescript"
            elif attr_name in ["attr_creation_date", "attr_modification_date"]:
                final_customer[sap_fieldname] = c[attr_name].strftime('%Y%m%d')
            elif attr_name == "attr_phone":
                final_customer[sap_fieldname] = "+" + str(c["phone_prefix"]) + " " + str(c["phone_suffix"])
            else:
                final_customer[sap_fieldname] = c[attr_name]

        final_customer["info_internal_id"] = c["info_internal_id"]
        final_customer["info_is_from"] = c["info_is_from"]
        # final_customer["info_altering"] = c["info_altering"]

        final_customers.append(final_customer)

    return pd.DataFrame(final_customers)


#######################################
# Split with overlap
#######################################

def split_customers_with_overlap(cfg: DictConfig, customers: list[Customer], overlap_percentage: float):
    num_overlap_customers = int(overlap_percentage * len(customers))
    logger.info(
        f"{overlap_percentage * 100}% overlap: Will have {num_overlap_customers} overlapping customers out of {len(customers)} total customers")

    # split with stepsize to make deterministic over multiple dataset sizes:
    step_size = cfg.dataset.split_step_size
    logger.info(f"Will split with step size {step_size}")

    overlap_total = 0
    company_A_customers = []
    company_B_customers = []
    overlap_customers = []
    for i in range(0, len(customers), step_size):
        batch_customers = customers[i: i + step_size]

        num_overlap_customers = int(overlap_percentage * len(batch_customers))
        overlap_total += num_overlap_customers

        batch_overlap_customers = batch_customers[:num_overlap_customers]
        if not len(batch_overlap_customers) == num_overlap_customers:
            logger.error(
                f"Want to have {num_overlap_customers} overlap customers but have only {len(batch_overlap_customers)}")
        overlap_customers += batch_overlap_customers
        remaining_customers = batch_customers[num_overlap_customers:]

        # num_customers_per_list = int(len(remaining_customers) / 2)

        # company_A_customers += remaining_customers[:num_customers_per_list]
        company_B_customers += remaining_customers  # [num_customers_per_list:]

    logger.info(
        f"Created {len(company_A_customers)} A and {len(company_B_customers)} B unique customers and {len(overlap_customers)} overlapping")

    for c in company_A_customers:
        c["info_is_from"] = "A"
    for c in company_B_customers:
        c["info_is_from"] = "B"
    for c in overlap_customers:
        c["info_is_from"] = "overlap"

    return overlap_customers, company_A_customers, company_B_customers


#######################################
# Company A
#######################################

def bring_customer_into_company_A_format(c: Customer, context: Context, cfg: DictConfig):
    final_customer = {}
    for (attr_name, config_values) in cfg.dataset.company_A_attributes.items():
        try:
            sap_fieldname = config_values["name"]
            # some fields have placeholder values and need to be filled here
            if attr_name == "attr_customerID":
                customer_id = create_new_customer_id(context.customer_ids_in_A, limit_for_A=True)
                context.customer_ids_in_A.append(customer_id)
                final_customer[sap_fieldname] = customer_id
            elif attr_name == "attr_creation_name":
                final_customer[sap_fieldname] = random.choice(context.creation_user_names_A)
            elif attr_name == "attr_creation_date":
                final_customer[sap_fieldname] = c[attr_name].strftime('%Y%m%d')
            elif attr_name == "attr_modification_date":
                final_customer[sap_fieldname] = c[attr_name].strftime('%Y%m%d')
            else:
                final_customer[sap_fieldname] = c[attr_name]
        except KeyError as e:
            if attr_name == "attr_phone":
                final_customer[sap_fieldname] = "+" + str(c["phone_prefix"]) + " " + str(c["phone_suffix"])
            else:
                print(f"Company A format: {e} Could not find {attr_name}")
        except Exception as e:
            print(f"Company A format: {e}")

    return final_customer


def generate_customer_A_table(customers: list[Customer], overlap_customers: list[Customer], context: Context,
                              cfg: DictConfig):
    """
    Generate the table of company A 
    """
    final_customers = []
    for c in customers:
        final_customer = bring_customer_into_company_A_format(c, context=context, cfg=cfg)
        final_customer["info_internal_id"] = c["info_internal_id"]
        final_customer["info_is_from"] = c["info_is_from"]
        final_customer["info_is_altered"] = False
        final_customers.append(final_customer)

    for o in overlap_customers:
        alter_customer = False
        if o["info_alter_datapoint"] == "A":
            alter_customer = True

        altering_info = None
        if alter_customer:
            o, altering_info = perform_customer_altering(customer=o, context=context, cfg=cfg)

        final_customer = bring_customer_into_company_A_format(c=o, context=context, cfg=cfg)
        final_customer["info_internal_id"] = o["info_internal_id"]
        final_customer["info_is_from"] = o["info_is_from"]
        final_customer["info_is_altered"] = alter_customer
        final_customer["info_altering"] = altering_info
        final_customers.append(final_customer)

    random.shuffle(final_customers)

    return final_customers


###########################
# Company B
###########################

def bring_customer_into_company_B_format(customer: Customer, context: Context, cfg: DictConfig):
    customer_info = {}
    customer_contact_details = {}

    attr_names = cfg.dataset.company_B_tables.customer_information

    if random.random() <= cfg.dataset.percentages.customer_id_reoccurs:
        is_unique = False
        # re-use customer-ID from company A
        while not is_unique:
            customer_id = random.choice(context.customer_ids_in_A)
            if customer_id not in context.customer_ids_in_B:
                is_unique = True
                context.customer_ids_in_B.append(customer_id)
    else:
        # create new customer-ID
        customer_id = create_new_customer_id(context.customer_ids_in_B)
        context.customer_ids_in_B.append(customer_id)

    customer_info[attr_names.attr_customerID.name] = customer_id
    customer_info[attr_names.attr_account.name] = cfg.dataset.account_groups[customer["attr_account"]]
    customer_info[attr_names.attr_role.name] = random.choice(["0001", "0002", "0003", "0004", "0005"])
    customer_info[attr_names.attr_contract.name] = random.choice([0, 1])  # contract is 0 or 1
    customer_info[attr_names.attr_creation_date.name] = customer["attr_creation_date"]
    # customer_info[attr_names.attr_creation_name.name] = random.choice(context.creation_user_names_B)
    customer_info[attr_names.attr_modification_date.name] = customer["attr_modification_date"]

    if customer["attr_tax_vat"]:
        tax_number = customer["attr_tax_vat"]
    else:
        tax_number = customer["attr_tax_other"]
    customer_info[attr_names.attr_tax_number.name] = tax_number

    customer_info["info_internal_id"] = customer["info_internal_id"]
    customer_info["info_is_altered"] = customer["info_is_altered"]
    customer_info["info_altering"] = customer["info_altering"]

    attr_names = cfg.dataset.company_B_tables.customer_contact_details

    customer_contact_details[attr_names.attr_customerID.name] = customer_id  # use same ID as in other table
    customer_contact_details[attr_names.attr_name.name] = customer["attr_name"]

    address = customer["attr_street"] + " " + customer["attr_zipcode"] + " " + customer["attr_city"] + ", " + customer[
        "attr_country_name"]
    customer_contact_details[attr_names.attr_address.name] = address
    customer_contact_details[attr_names.attr_email.name] = customer["attr_email"]
    customer_contact_details[attr_names.attr_phone_prefix.name] = customer["phone_prefix"]
    customer_contact_details[attr_names.attr_phone_number.name] = customer["phone_suffix"]

    return customer_info, customer_contact_details


def generate_customer_B_tables(customers: list[Customer], overlap_customers: list[Customer], context: Context,
                               cfg: DictConfig):
    customers_information = []
    customers_contact_details = []
    all_customers = []

    for c in customers:
        c["info_is_altered"] = False
        c["info_altering"] = None
        info, contact = bring_customer_into_company_B_format(customer=c, context=context, cfg=cfg)

        customers_information.append(info)
        customers_contact_details.append(contact)
        all_customers.append(c.copy())

    for o in overlap_customers:
        alter_customer = False
        if o["info_alter_datapoint"] == "B":
            alter_customer = True

        altering_info = None
        if alter_customer:
            o, altering_info = perform_customer_altering(customer=o, context=context, cfg=cfg)

        o["info_is_altered"] = alter_customer
        o["info_altering"] = altering_info
        all_customers.append(o.copy())

        info, contact = bring_customer_into_company_B_format(customer=o, context=context, cfg=cfg)

        customers_information.append(info)
        customers_contact_details.append(contact)

    random.shuffle(customers_information)
    random.shuffle(customers_contact_details)

    return customers_information, customers_contact_details, all_customers


#################################
# Main - Create Dataset
#################################

def custom_serializer(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()  # Convert dates and datetimes to ISO 8601 format
    else:
        raise TypeError(f"Type {type(obj)} not serializable")


@hydra.main(version_base=None, config_path="../../../config/compound_task", config_name="config.yaml")
def main(cfg: DictConfig) -> None:
    assert cfg.dataset.dataset_name == "customer_integration", "This script is dataset-specific."
    download_dir = get_download_dir(cfg.task_name, cfg.dataset.dataset_name, clear=False)

    context = Context.empty()

    save_folder = f"{cfg.dataset.total_num_customers}_customers_{cfg.dataset.percentages.matches}_overlap_{cfg.dataset.percentages.discrepancies}_discrepancies_{cfg.dataset.percentages.alter_attribute}_altering"
    os.makedirs(download_dir / save_folder, exist_ok=True)

    # create some random user names
    context.creation_user_names_A = [random_sap_number(12) for i in range(cfg.dataset.num_creation_user_names)]
    context.creation_user_names_B = ["".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(6))
                                     for i in range(cfg.dataset.num_creation_user_names)]

    # create all the customers
    for i in range(cfg.dataset.total_num_customers):
        generate_customer(context, cfg)

    # split customers into two parts with given overlap
    assert cfg.dataset.percentages.matches >= 0 and cfg.dataset.percentages.matches <= 1
    overlap_customers, only_company_A_customers, only_company_B_customers = split_customers_with_overlap(cfg=cfg,
                                                                                                         customers=context.customers,
                                                                                                         overlap_percentage=cfg.dataset.percentages.matches)

    with open(download_dir / save_folder / "data_info_ids.json", "w") as file:
        json.dump({"overlap": [i['info_internal_id'] for i in overlap_customers],
                   "only_A": [i['info_internal_id'] for i in only_company_A_customers],
                   "only_B": [i['info_internal_id'] for i in only_company_B_customers]}, file, indent=2,
                  default=custom_serializer)

    # decide for which company a datapoint should be altered
    for o in overlap_customers:
        if random.random() <= cfg.dataset.percentages.discrepancies:
            if random.random() < 0.5:
                o["info_alter_datapoint"] = "A"
            else:
                o["info_alter_datapoint"] = "B"
        else:
            o["info_alter_datapoint"] = "No"

    # alter company A customers and bring in correct format
    company_A_customers = generate_customer_A_table(only_company_A_customers, overlap_customers, context, cfg)

    # alter company B customers and bring in correct format
    company_B_customers_info, company_B_customers_contact, company_B_all_customers = generate_customer_B_tables(
        only_company_B_customers, overlap_customers, context, cfg)

    # create final output table by bringing all customers into KNA-1 format 
    final_df = generate_final_table(context.customers, company_A_customers, cfg=cfg)

    # asserts in final output table:
    assert final_df["TELF1"].is_unique
    assert final_df["SMTP_ADDR"].is_unique
    assert pd.concat([final_df["STCEG"], final_df["STCD1"]]).dropna().is_unique

    final_df.to_csv(download_dir / save_folder / "ground_truth_table.csv", index=False, sep=";")

    # save final company dataframes:
    company_A_df = pd.DataFrame(company_A_customers)

    company_B_info_df = pd.DataFrame(company_B_customers_info)
    company_B_contact_df = pd.DataFrame(company_B_customers_contact)
    assert len(company_B_info_df) == len(company_B_contact_df)

    company_A_df.to_csv(download_dir / save_folder / "company_A_table.csv", index=False, sep=";")
    company_B_info_df.to_csv(download_dir / save_folder / "company_B_table_info.csv", index=False, sep=";")
    company_B_contact_df.to_csv(download_dir / save_folder / "company_B_table_contact.csv", index=False, sep=";")

    logger.info(f"Table length: A {len(company_A_df)}, B: {len(company_B_info_df)}")

    # save company B joined table
    company_B_joined = pd.merge(company_B_info_df, company_B_contact_df, left_on="ID", right_on="Customer ID",
                                how="inner")
    company_B_joined = company_B_joined.drop(columns="ID")
    company_B_joined.to_csv(download_dir / save_folder / "company_B_table_joined.csv", index=False, sep=";")

    customers_df = pd.DataFrame(context.customers)
    customers_df.to_csv(download_dir / save_folder / "all_customers.csv", index=False, sep=";")

    # save input & output (ground truth) for data transformation
    # bring the data from company B into the format from company A
    data_transformation_all = company_A_customers
    for c in company_B_all_customers:
        final_customer = bring_customer_into_company_A_format(c, context=context, cfg=cfg)
        final_customer["info_internal_id"] = c["info_internal_id"]
        final_customer["info_is_from"] = c["info_is_from"]
        final_customer["info_is_altered"] = c["info_is_altered"]
        final_customer["info_altering"] = c["info_altering"]
        data_transformation_all.append(final_customer)
    data_transformation_all_df = pd.DataFrame(data_transformation_all)
    data_transformation_all_df.to_csv(download_dir / save_folder / "GT_data_transformation.csv", index=False, sep=";")

    # Info: input & output (ground truth) for deduplication task is given with internal ID

    # save input & output (ground truth) for entity matching task
    # save internal IDs that are present in both companies:
    entity_matching_info = {"matches": []}
    for o in overlap_customers:
        entity_matching_info["matches"].append({"info_internal_id": o["info_internal_id"],
                                                "altered_in": o["info_alter_datapoint"]})

    with open(download_dir / save_folder / "GT_entity_matching.json", "w") as file:
        json.dump(entity_matching_info, file, indent=2)

    # create three more new customers as example data in A
    context.customers = []
    for i in range(3):
        generate_customer(context, cfg)
    for c in context.customers:
        c["info_is_from"] = "A"
    # alter company A customers and bring in correct format
    example_customers = generate_customer_A_table(context.customers, [], context, cfg)
    # save final company dataframes:
    example_df = pd.DataFrame(example_customers)
    example_df.to_csv(download_dir / save_folder / "examples_company_A.csv", index=False, sep=";")


if __name__ == "__main__":
    main()
