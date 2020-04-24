This script uses selenium to scrape linkedin employee details from a specified company.  If the script isn't working, you can always browse to the desired company's employee page and paste in the link on line 69 like this: "employees_page = url"

The trick is to run the script with the "--function get" flag first.  When the browser has opened and run through it's tests, and the files have been successfully saved on disk, then re-run the script using the "--function create" flag.  

Working as of now. This script prints out a list of permutations for possible working emails for a company. It can be used in combination with my email_checker.py script to verify outlook mails. On the first run you will need to manually input the 6-digit code sent to your email, then rerun the script. This needs to be done once per device.

```sh
# Linkedin_profiles  
scrapes Linkedin for company employee profiles  
  
usage: linkedin_profiles.py [-h] --company COMPANY --email_suffix EMAIL_SUFFIX  
                            --email_prefix  
                            {full,namenname,nname,nnname,namename,name.name,namen}  
                            --function {get,create} --ignore  
  
Scrape Linkedin profiles for a specified company  
  
optional arguments:  
  -h, --help            show this help message and exit  
  --company COMPANY     The name of the company on Linkedin  
  --email_suffix EMAIL_SUFFIX  
                        The company email suffix ex: user@<email_suffix>  
  --email_prefix {full,namenname,nname,nnname,namename,name.name,namen}
                        The email prefix format ex: <email_prefix>@company.com
                         full   - ex: johntimothydoe@company.com
                         namenname - ex: johntdoe@company.com
                         nname  - ex: jdoe@company.com
                         nnname - ex: jtdoe@company.com
                         namename - ex: johndoe@company.com
                         name.name - ex: john.doe@company.com namen - ex: johnd@company.com
  --function {get,create}  
                         Function to perform:    
                         get - Logs into Linkedin and saves the employee html pages  
                         create - Parses the html pages to create employee lists  
  --ignore              Ignore profiles without a name 
```
