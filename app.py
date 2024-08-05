import argparse
import requests
import json
import os

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

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

def get_apps(api_url, api_key):
    url = f"{api_url}/dynamic/get_apps"
    headers = {'Authorization': api_key}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting apps: {e}")
        return None

def start_dynamic_analysis(api_url, api_key, file_hash):
    url = f"{api_url}/dynamic/start_analysis"
    headers = {'Authorization': api_key}
    data = {'hash': file_hash}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error starting dynamic analysis: {e}")
        return None

def stop_dynamic_analysis(api_url, api_key, file_hash):
    url = f"{api_url}/dynamic/stop_analysis"
    headers = {'Authorization': api_key}
    data = {'hash': file_hash}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error stopping dynamic analysis: {e}")
        return None

def main(file_path, api_key, api_url, analysis_type):
    if not api_url or not api_key:
        print("API URL or API Key missing.")
        return

    file_hash = upload_file(api_url, api_key, file_path)
    if file_hash:
        print(f"File uploaded successfully. Hash: {file_hash}")

        if analysis_type in ['static', 'both']:
            if trigger_scan(api_url, api_key, file_hash):
                print("Static scan triggered successfully.")
                report = fetch_report(api_url, api_key, file_hash)
                if report:
                    save_json_report(report, '/output')
                    download_pdf_report(api_url, api_key, file_hash, '/output')
                else:
                    print("Failed to fetch JSON report.")
            else:
                print("Failed to trigger static scan.")

        if analysis_type in ['dynamic', 'both']:
            apps = get_apps(api_url, api_key)
            if apps:
                print("Apps retrieved successfully.")
                dynamic_result = start_dynamic_analysis(api_url, api_key, file_hash)
                if dynamic_result:
                    print("Dynamic analysis started successfully.")
                    stop_result = stop_dynamic_analysis(api_url, api_key, file_hash)
                    if stop_result:
                        print("Dynamic analysis stopped successfully.")
                    else:
                        print("Failed to stop dynamic analysis.")
                else:
                    print("Failed to start dynamic analysis.")
            else:
                print("Failed to retrieve apps.")
    else:
        print("Failed to upload file.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload APK file to MobSF, trigger scan, and fetch JSON and PDF reports.')
    parser.add_argument('file', type=str, help='Path to the APK file (located in /apk directory)')
    parser.add_argument('--api-key', required=True, type=str, help='API Key for accessing the MobSF API')
    parser.add_argument('--api-url', required=True, type=str, help='URL of the MobSF API')
    parser.add_argument('--analysis-type', choices=['static', 'dynamic', 'both'], default='both', help='Type of analysis to perform')
    args = parser.parse_args()
    main(args.file, args.api_key, args.api_url, args.analysis_type)
