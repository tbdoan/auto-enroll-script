from typing import Tuple
import requests
from bs4 import BeautifulSoup


def login(user,pw):
    def extract_sso_url(res : requests.Response) -> str:
        soup = BeautifulSoup(str(res.content), 'html.parser')
        return 'https://a5.ucsd.edu' + soup.find(id='login')['action']

    def extract_duo_url(res: requests.Response) -> Tuple[str,str]:
        soup = BeautifulSoup(str(res.content), 'html.parser')
        form = soup.find(id='duo_iframe')
        host = form['data-host']
        base_url = 'https://' + host + '/frame/web/v1/auth'
        data_sig_req = form['data-sig-request']
        data_post_act = form['data-post-action']
        tx,_,_ = data_sig_req.partition(':APP')
        params = {
            'tx': tx,
            'parent': 'https://a5.ucsd.edu' + data_post_act,
            'v': '2.3'
        }
        r = requests.get(base_url, params=params)
        return r.url,tx

    def extract_sid(res: requests.Response) -> str:
        soup = BeautifulSoup(str(res.content), 'html.parser')
        sid = soup.find_all(attrs={"name": "sid"})[0]['value']
        return sid

    def construct_login_headers(referer_url):
        return {
            'Connection': 'keep-alive',
            'Origin': 'https://a5.ucsd.edu',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': referer_url
        }

    def construct_login_payload(user,pw):
        return {
            'urn:mace:ucsd.edu:sso:username': user,
            'urn:mace:ucsd.edu:sso:password': pw,
            '_eventId_proceed': ''
        }

    def construct_duo_headers(referer_url):
        return {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://api-ce13a1a7.duosecurity.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': referer_url
        }

    def construct_duo_payload(tx_string):
        return {
            'tx': tx_string,
            'parent': 'https://a5.ucsd.edu/tritON/profile/SAML2/Redirect/SSO?execution=e1s2',
            'java_version': '',
            'flash_version': '',
            'screen_resolution_width': '1440',
            'screen_resolution_height': '900',
            'color_depth': '30',
            'is_cef_browser': 'false',
            'is_ipad_os': 'false',
            'is_ie_compatibility_mode': '',
            'is_user_verifying_platform_authenticator_available': 'true',
            'user_verifying_platform_authenticator_available_error': '',
            'acting_ie_version': '',
            'react_support': 'true',
            'react_support_error_message': '',
        }

    s = requests.Session()
    # go to login page
    sso_res = s.get('https://act.ucsd.edu/webreg2')
    # construct login info
    sso_url = extract_sso_url(sso_res)
    login_headers = construct_login_headers(sso_url)
    payload = construct_login_payload(user,pw)
    # send login info
    two_step_res = s.post(
        'https://a5.ucsd.edu/tritON/profile/SAML2/Redirect/SSO?execution=e1s1',
        headers=login_headers,
        data=payload
    )
    # constructs duo info
    duo_url,tx_string = extract_duo_url(two_step_res)
    duo_headers = construct_duo_headers(duo_url)
    duo_payload = construct_duo_payload(tx_string)
    duo_res = requests.post(
        duo_url,
        headers=duo_headers,
        data=duo_payload
    )
    sid = extract_sid(duo_res)
    print(sid)
    s.close()

def enroll(*,cookie,section,grade='L',unit,subjcode,crsecode,termcode):
    def generate_enroll_headers(cookie):
        cookie_string = f'jlinksessionidx={cookie}'
        return {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://act.ucsd.edu',
        'Referer': 'https://act.ucsd.edu/webreg2/main',
        'Cookie': cookie_string
    }
    def generate_payload(section,grade,unit,subjcode,crsecode,termcode):
        return {
            'section': section,
            'grade': grade,
            'unit': unit,
            'subjcode': subjcode,
            'crsecode': crsecode,
            'termcode': termcode
        }
    s = requests.Session()
    enroll_url = 'https://act.ucsd.edu/webreg2/svc/wradapter/secure/add-enroll'
    enroll_headers = generate_enroll_headers(cookie)
    enroll_payload = generate_payload(section,grade,unit,subjcode,crsecode,termcode)
    res = s.post(enroll_url, headers=enroll_headers,data=payload)
    sso_html_text = str(res.content)
    soup = BeautifulSoup(sso_html_text, 'html.parser')
    login_form_element = soup.find(id='login')
    login_url = 'https://a5.ucsd.edu' + login_form_element['action']
    login_headers = enroll_headers.copy()
    #login_headers =
    s.post(login_url,headers=login_headers)

## MAIN ##
#username = input("Enter your username: ")
#password = input("Enter your password: ")

login('tbdoan','Wowzer1213')

