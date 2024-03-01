# CRM Project by Mike-Mining

import pandas as pd
from datetime import datetime
import time
import requests 
import logging

firm_reference_number: list[str] = ['161227']

def api_call(frn:str) -> pd.DataFrame:
    email_address = 'YOUR_EMAIL_ADDRESS'
    api_key = 'YOUR_API_KEY'
    base_url : str = 'https://register.fca.org.uk/services/V0.1/'
    url = base_url + f'Firm/{frn}'
    headers = {'X-AUTH-EMAIL': email_address,'X-AUTH-KEY': api_key,'Content-Type':'application/json'}
    api_status_code : dict = { 'FSR-API-02-01-11':'Bad Request : Invalid Input'
                              ,'FSR-API-02-01-21':'ERROR : Account Not Found'
                              ,'FSR-API-01-01-11':'Unauthorised: Please include a valid API key and Email address'}
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()  # Raise an HTTPError for bad responses
        
        if r.status_code != 200:
            logging.error(f"API call for FRN {frn} failed with status code {r.status_code}")
            return pd.DataFrame()
        
        json_data = r.json()

        if json_data['Status'] in api_status_code:
            logging.error(f"API call for FRN {frn} failed with status {json_data['Status']} and {api_status_code[json_data['Status']]}")
            return pd.DataFrame()

        json_data2 = pd.json_normalize(json_data['Data'][0])
        return json_data2
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making API call for FRN {frn}: {e}")
        return pd.DataFrame()
    
def df_data(api_data:pd.DataFrame):
    if not api_data.empty:
        #column_names: list[str] = ['Customer Engagement Method', 'Suspension / Restriction End Date', 'Suspension / Restriction Start Date', 'Restriction', 'Effective Date', 'Firm Name', 'Name', 'URL']
        df = pd.DataFrame(api_data)#, columns=column_names)
        # Get the current date and time
        current_datetime = datetime.now()
        # Format the date and time as yyyy_mm_dd_hh_mm_ss
        formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
        df.to_csv(f'FCA_Firm_Details {formatted_datetime}.csv', index=False)
        
    else:
        logging.warning("Empty DataFrame received. Skipping reshaping and CSV creation.")

# Example function to get company information by company number
def get_company_info(company_number):
    print(company_number)
    # Replace 'YOUR_API_KEY' with your actual Companies House API key
    api_key : str = 'YOUR_API_KEY'
    base_url : str = 'https://api.companieshouse.gov.uk/'
    url = base_url + f'company/{company_number}'
    headers = {'Authorization': api_key}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        company_data = response.json()
        if company_data:
            print(f"Company Name: {company_data['company_name']}")
            print(f"Registered Office: {company_data['registered_office_address']}")
            print(f"Date of Creation: {company_data['date_of_creation']}")
            print(f"SIC Codes: {company_data['sic_codes']}")
            print(f"Company Status: {company_data['company_status']}")
            print(f"Company Type: {company_data['type']}")
        else:
            print("Failed to retrieve company information.")
            return company_data
    else:
        print(f"Error: {response.status_code}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # Set the logging level
    print(datetime.now())
    
    for frn in firm_reference_number:
        api_data = api_call(frn)
        df_data(api_data)
        get_company_info(api_data['Companies House Number'][0])
        print(frn)
    print('Hello World')