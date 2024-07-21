import argparse
import requests
import json
import os

def upload_file(api_url, api_key, file_path):
    upload_url = f"{api_url}/upload"
    headers = {'Authorization': api_key}
    file_name = os.path.basename(file_path)
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (file_name, file, 'application/vnd.android.package-archive')}
            response = requests.post(upload_url, headers=headers, files=files)
            response.raise_for_status()
            return response.json().get('hash')
    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e}")
        return None

def trigger_scan(api_url, api_key, file_hash):
    scan_url = f"{api_url}/scan"
    headers = {'Authorization': api_key}
    data = {'hash': file_hash}
    
    try:
        response = requests.post(scan_url, headers=headers, data=data)
        response.raise_for_status()
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Error triggering scan: {e}")
        return False

def fetch_report(api_url, api_key, file_hash):
    report_url = f"{api_url}/report_json"
    headers = {'Authorization': api_key}
    data = {'hash': file_hash}
    
    try:
        response = requests.post(report_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching report: {e}")
        return None

def download_pdf_report(api_url, api_key, file_hash, output_dir, filename='mob_sf_report.pdf'):
    pdf_url = f"{api_url}/download_pdf"
    headers = {'Authorization': api_key}
    data = {'hash': file_hash}
    
    try:
        response = requests.post(pdf_url, headers=headers, data=data)
        response.raise_for_status()
        
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(response.content)
        
        print(f"PDF report saved to {file_path}.")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF report: {e}")

def save_json_report(report, output_dir, filename='mob_sf_report.json'):
    try:
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'w') as json_file:
            json.dump(report, json_file, indent=4)
        print(f"JSON report saved to {file_path}.")
    except IOError as e:
        print(f"Error saving JSON report: {e}")

def main(file_path, api_key, api_url):
    output_dir = os.path.join(os.path.dirname(file_path), 'output')
    
    file_hash = upload_file(api_url, api_key, file_path)
    if file_hash:
        print(f"File uploaded successfully. Hash: {file_hash}")
        if trigger_scan(api_url, api_key, file_hash):
            print("Scan triggered successfully.")
            report = fetch_report(api_url, api_key, file_hash)
            if report:
                save_json_report(report, output_dir)
                download_pdf_report(api_url, api_key, file_hash, output_dir)
            else:
                print("Failed to fetch JSON report.")
        else:
            print("Failed to trigger scan.")
    else:
        print("Failed to upload file.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload APK file to MobSF, trigger scan, and fetch JSON and PDF reports.')
    parser.add_argument('file', type=str, help='Path to the APK file')
    parser.add_argument('--api-key', required=True, type=str, help='API Key for accessing the MobSF API')
    parser.add_argument('--api-url', required=True, type=str, help='URL of the MobSF API')
    args = parser.parse_args()
    main(args.file, args.api_key, args.api_url)
