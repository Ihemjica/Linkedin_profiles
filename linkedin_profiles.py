# -*- coding: utf-8 -*-
from selenium import webdriver
import sys
import traceback
import json
import argparse
import requests
import os
import re

reload(sys)
sys.setdefaultencoding('utf8')

class LinkedinProfiles():
    def __init__(self, company, email_suffix):
        self.base_url = "https://www.linkedin.com/login"
        self.verificationErrors = []
        self.accept_next_alert = True
        self.employees = []
        self.company = company
        self.website = email_suffix
        self.scompany = company.replace(" ", "_")
        if not os.path.isdir(self.scompany):
            os.mkdir(self.scompany)

    def init_driver(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(15)
        self.username = raw_input('linkedin username:')
        self.password = raw_input('linkedin password:')

    # This function will open the browser, login to linkedin, then save all search results for the company
    # specified in the company variable
    def get_linkedin_profiles(self):
        self.init_driver()
        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_id("username").clear()
        driver.find_element_by_id("username").send_keys(self.username)
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(self.password)
        driver.find_element_by_class_name("btn__primary--large").click()

        # driver.find_element_by_name("submit").click()
        #driver.find_element_by_class_name("search-global-typeahead__input").clear()
        #driver.find_element_by_class_name("search-global-typeahead__input").send_keys(self.company)
        # Create the search URL
        search = "https://www.linkedin.com/voyager/api/typeahead/hitsV2"
        params = {'q': 'blended',
                  'keywords': self.company}
        # search = "https://www.linkedin.com/ta/federator?orig=GLHD&verticalSelector=all&query={}&tracking=true&refTarId=1468332198550"
        JSESSIONID = driver.get_cookie('JSESSIONID')['value']
        LI_AT = driver.get_cookie('li_at')['value']
        driver.close()
        cookies = {'JSESSIONID' : JSESSIONID.strip('"'),
                   'li_at' : str(LI_AT)}
        headers = {'csrf-token' : JSESSIONID.strip('"')}
        # print JSESSIONID,LI_AT,cookies,headers
        r = requests.get(search, params=params, cookies=cookies, headers=headers)
        # print JSESSIONID,LI_AT,r.text
        # Parse the results from our search
        #soup = BeautifulSoup(driver.page_source)
        j = json.loads(r.text)
        # Results look like: {"meta":{"tarId":"1468332203875"},"resultList":[{"sourceID":"autocomplete","displayName":"cottingham butler","subLine":"","rank":0,"id":"1","url":"","headLine":"cottingham butler"},{"sourceID":"company","displayName":"Cottingham &amp; Butler","imageUrl":"https://media.licdn.com/mpr/mpr/shrink_100_100/p/5/000/226/18c/395b088.png","subLine":"Insurance; 501-1000 employees","rank":1,"id":"54611","url":"https://www.linkedin.com/company/54611","headLine":"Cottingham &amp; Butler"},{"sourceID":"group","displayName":"Cottingham &amp; Butler Transportation Summit","imageUrl":"https://media.licdn.com/mpr/mpr/shrink_100_100/p/6/005/049/120/046d523.png","subLine":"","rank":2,"id":"6641194","url":"https://www.linkedin.com/groups?gid=6641194&mostPopular=","headLine":"Cottingham &amp; Butler Transportation Summit"},{"sourceID":"mynetwork","displayName":"Cottingham Butler","subLine":"Sales Executive at Cottingham and Butler","rank":3,"id":"471545431","url":"https://www.linkedin.com/profile/view?id=AAkAABwbNlcBBLH-e2KL__V9-v0Z3h6Aiflxec0&authType=NAME_SEARCH&authToken=mhR4&locale=en_US","headLine":"Cottingham Butler","misc":{"degree":""}}]}
        comp_id = None
        for item in j['elements']:
            # Select the company that matches the given website
            if item['type'] == 'COMPANY':
                comp_id = int(item['targetUrn'].split(':')[-1])
                r = requests.get("https://www.linkedin.com/company/{}/about/".format(comp_id), cookies=cookies, headers=headers)
                r1 = len(re.findall(self.website,r.text))
                if r1 > 0:
                    break
            else:
                continue
        if comp_id:
            # Add additional header for getting the company's employee search
            headers.update({'x-restli-protocol-version': '2.0.0'})
            #employees_page = "https://www.linkedin.com/voyager/api/search/blended?count=40&filters=List(currentCompany-%3E{},resultType-%3EPEOPLE)&origin=OTHER&q=all&start=0".format(comp_id)
        else:
            print "Couldn't find a company link with that name! Quitting..."
            quit()
        # driver.get(employees_page)
        # driver.find_element_by_xpath('//*[@id="results"]/li[1]/div/h3/a').click()
        # driver.find_element_by_link_text("See all").click()
        previous = ""
        for i in range(0, 1000, 40):
            #sleep(5)
            f = open("{}/{}{}_source.html".format(self.scompany, self.scompany, i/40), 'wb')
            source = requests.get("https://www.linkedin.com/voyager/api/search/blended?count=40&filters=List(currentCompany-%3E{},resultType-%3EPEOPLE)&origin=OTHER&q=all&start={}".format(comp_id, i), cookies=cookies, headers=headers)
            # In case there's no more data the size of the response will be less than 200 characters
            if len(source.text) < 400:
            	print "Pulled {} pages".format((i/40)+1)
                break
            #encoded = source.encode('utf-8').strip()
            f.write(source.text)
            f.close()
        # driver.find_element_by_link_text("Next >").click()
        # driver.find_element_by_link_text("Next >").click()

class ParseProfiles():
    def __init__(self, suffix, prefix, ignore, company):
        self.employees = []
        self.prefix = prefix
        self.suffix = suffix
        self.ignore = ignore
        self.company = company.replace(" ", "_")

    def parse_source(self, path):
        try:
            source = open(path)
            #print path
            data = json.load(source)
            links = data['elements'][0]['elements']
            # data["elements"][0]["elements"][37]["image"]["attributes"][0]["miniProfile"]["picture"]["com.linkedin.common.VectorImage"]["rootUrl"]+data["elements"][0]["elements"][37]["image"]["attributes"][0]["miniProfile"]["picture"]["com.linkedin.common.VectorImage"]["artifacts"][-1]["fileIdentifyingUrlPathSegment"]
            #links = results.find_all("li", {"class": "mod"})
            for person in links:
                #link = person.find('a', {"class": "result-image"})
                ind = {'firstName': "Not Found",
                       'picture': "Not Found",
                       'lastName': "Not Found",
                       'name': "Not Found",
                       'email': [],
                       'job': "Not Found"}
                #if link:
                #    # img = link.img
                #    img = link
                #if img:
                    # ind['picture'] = img.get('src')
                try:
                    ind['picture'] = person['image']['attributes'][0]['miniProfile']['picture']['com.linkedin.common.VectorImage']['rootUrl']+person['image']['attributes'][0]['miniProfile']['picture']['com.linkedin.common.VectorImage']['artifacts'][-1]['fileIdentifyingUrlPathSegment']
                except Exception, e:
                    ind['picture'] = "Not Found"
                #name = person.find('a', {"class": "title main-headline"})
                #print ind['picture']
                ind['firstName'] = person['image']['attributes'][0]['miniProfile']['firstName'].strip()
                ind['lastName'] = person['image']['attributes'][0]['miniProfile']['lastName'].strip()
                ind['name'] = "{} {}".format(ind['firstName'], ind['lastName'])
                ind['job'] = person['image']['attributes'][0]['miniProfile']['occupation']
                # print ind['name']
                self.employees.append(ind)
        except Exception, e:
            print "Encountered error parsing file: {}".format(path)
            traceback.print_exc(e)

    def print_employees(self):
        body = ""
        emails = []
        csv = []
        header = "<table>" \
                 "<thead>" \
                 "<tr>" \
                 "<td>Picture</td>" \
                 "<td>Name</td>" \
                 "<td>Possible Email:</td>" \
                 "<td>Job</td>" \
                 "</tr>" \
                 "</thead>"
        #print self.employees
        for emp in self.employees:
            if ',' in emp['name']:
                print "user's name contains a comma, might not display properly: {}".format(emp['name'])
            name = emp['name'].split(',')[0].strip()
            emp['name'] = name
            if '(' in emp['name']:
                print "user's name contains a bracket, might not display properly: {}".format(emp['name'])
            name = emp['name'].split('(')[0].strip()
            emp['name'] = name
            if ' - ' in emp['name']:
                print "user's name contains a spaced hypen, might not display properly: {}".format(emp['name'])
            name = emp['name'].split(' - ')[0].strip()

            users=[]
            parts = name.split()
            if emp['name'] != 'LinkedIn Member':
            	#print len(parts)
                if len(parts) == 2:
                    fname = parts[0]
                    mname = '?'
                    lname = parts[1]
                elif len(parts) == 3:
                    fname = parts[0]
                    mname = parts[1]
                    lname = parts[2]
                if not fname:
                    print hi
                    continue
                fname = re.sub('[^A-Za-z]+', '', fname)
                mname = re.sub('[^A-Za-z]+', '', mname)
                lname = re.sub('[^A-Za-z]+', '', lname)
                if self.prefix == 'namename':
                    users.append('{}{}'.format(fname, lname))
                    users.append('{}{}'.format(lname, fname))
                    if mname != '':
                        users.append('{}{}'.format(fname, mname))
                        users.append('{}{}'.format(lname, mname))
                        users.append('{}{}'.format(mname, lname))
                        users.append('{}{}'.format(mname, fname))
                if self.prefix == 'nname':
                    users.append('{}{}'.format(fname[0], lname))
                    users.append('{}{}'.format(lname[0], fname))
                    if mname != '':
                        users.append('{}{}'.format(fname[0], mname))
                        users.append('{}{}'.format(lname[0], mname))
                        users.append('{}{}'.format(mname[0], lname))
                        users.append('{}{}'.format(mname[0], fname))
                if self.prefix == 'namen':
                    users.append('{}{}'.format(fname, lname[0]))
                    users.append('{}{}'.format(lname, fname[0]))
                    if mname != '':
                        users.append('{}{}'.format(fname, mname[0]))
                        users.append('{}{}'.format(lname, mname[0]))
                        users.append('{}{}'.format(mname, lname[0]))
                        users.append('{}{}'.format(mname, fname[0]))
                if self.prefix == 'name.name':
                    users.append('{}.{}'.format(fname, lname))
                    users.append('{}.{}'.format(lname, fname))
                    if mname != '':
                        users.append('{}.{}'.format(fname, mname))
                        users.append('{}.{}'.format(lname, mname))
                        users.append('{}.{}'.format(mname, lname))
                        users.append('{}.{}'.format(mname, fname))
                if self.prefix == 'full':
                    if mname != '':
                        users.append('{}{}{}'.format(fname, mname, lname))
                        users.append('{}{}{}'.format(fname, lname, mname))
                        users.append('{}{}{}'.format(mname, fname, lname))
                        users.append('{}{}{}'.format(mname, lname, fname))
                        users.append('{}{}{}'.format(lname, fname, mname))
                        users.append('{}{}{}'.format(lname, mname, fname))
                if self.prefix == 'namenname':
                    if mname != '':
                        users.append('{}{}{}'.format(fname, mname[0], lname))
                        users.append('{}{}{}'.format(fname, lname[0], mname))
                        users.append('{}{}{}'.format(mname, fname[0], lname))
                        users.append('{}{}{}'.format(mname, lname[0], fname))
                        users.append('{}{}{}'.format(lname, fname[0], mname))
                        users.append('{}{}{}'.format(lname, mname[0], fname))
                if self.prefix == 'nnname':
                    if mname != '':
                        users.append('{}{}{}'.format(fname[0], mname[0], lname))
                        users.append('{}{}{}'.format(fname[0], lname[0], mname))
                        users.append('{}{}{}'.format(mname[0], fname[0], lname))
                        users.append('{}{}{}'.format(mname[0], lname[0], fname))
                        users.append('{}{}{}'.format(lname[0], fname[0], mname))
                        users.append('{}{}{}'.format(lname[0], mname[0], fname))         
                for user in users:
                    emp['email'].append('{}@{}'.format(user, self.suffix))
                    emails.append('{}@{}'.format(user, self.suffix))
                    
            # Only add the employee if we're not ignoring it
            if not self.ignore or (self.ignore and emp['name'] != 'LinkedIn Member'):
                body += "<tr>" \
                        "<td>{picture}</td>" \
                        "<td>{name}</td>" \
                        "<td>{email}</td>" \
                        "<td>{job}</td>" \
                        "<td>".format(**emp)
                csv.append('{picture};{name};{email};"{job}"'.format(**emp))
            else:
                print "ignoring user: {} - {}".format(emp['name'], emp['job'])
        foot = "</table>"
        f = open('{}/employees.html'.format(self.company), 'wb')
        f.write(header)
        f.write(body)
        f.write(foot)
        f.close()
        f = open('{}/employees.csv'.format(self.company), 'wb')
        f.writelines('\n'.join(csv))
        f.close()
        f=open('{}/employees.txt'.format(self.company), 'wb')
        f.writelines('\n'.join(emails))
        f.close()


class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)

def main():
    parser = argparse.ArgumentParser(description='Scrape Linkedin profiles for a specified company', formatter_class=SmartFormatter)
    parser.add_argument('--company', help='The name of the company on Linkedin', required=True)
    parser.add_argument('--email_suffix', help='The company email suffix ex: user@<email_suffix>', required=True)
    parser.add_argument('--email_prefix', choices=['full', 'namenname', 'nname', 'nnname', 'namename', 'name.name', 'namen'],
                        help='R|The email prefix format ex: <email_prefix>@company.com\n'
                             ' full   - ex: johntimothydoe@company.com\n'
                             ' namenname - ex: johntdoe@company.com\n'
                             ' nname  - ex: jdoe@company.com\n'
                             ' nnname - ex: jtdoe@company.com\n'
                             ' namename - ex: johndoe@company.com\n'
                             ' name.name - ex: john.doe@company.com'
                             ' namen - ex: johnd@company.com', required=True)
    parser.add_argument('--function', choices=['get', 'create'],
                        help='R| Function to perform:\n'
                             ' get - Logs into Linkedin and saves the employee html pages\n'
                             ' create - Parses the html pages to create employee lists', required=True)
    parser.add_argument('--ignore', help='Ignore profiles without a name', action='store_true', required=True)
    args = parser.parse_args()
    company = args.company.replace(" ", "_")

    if args.function == 'create':
        # Parse the downloaded page sources
        pp = ParseProfiles(args.email_suffix, args.email_prefix, args.ignore, args.company)
        for i in range(0, 25):
            filename = "{}{}_source.html".format(company, i)
            file_path = "{}/{}".format(company, filename)
            if os.path.isfile(file_path):
                pp.parse_source(file_path)
            else:
                print "file {} not found, stopping...".format(file_path)
                break
        pp.print_employees()

    elif args.function == 'get':
        lip = LinkedinProfiles(args.company, args.email_suffix)
        # Start the web driver and download the company's employee pages
        lip.get_linkedin_profiles()


if __name__ == "__main__":
    main()
    # test()
