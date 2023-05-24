# pip install pandas
# pip install requests
# pip install beautifulsoup4


import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from google.cloud import storage
from google.oauth2 import service_account
from sqlalchemy import create_engine


engine = create_engine("sqlite://")

def scrape_this(uri="/pages/forms/"):
  page = requests.get("https://scrapethissite.com" + uri)
  soup = BeautifulSoup(page.text, "html.parser")

  div = soup.find(id="hockey")  
  table = div.find("table")

  data_rows = table.find_all("tr", attrs={"class": "team"})
  parsed_data = list()
  stat_keys = [col.attrs["class"][0] for col in data_rows[0].find_all("td")]

  for row in data_rows:
    tmp_data = dict()
    for attr in stat_keys:
      attr_val = row.find(attrs={"class": attr}).text
      tmp_data[attr] = re.sub(r"^\s+|\s+$", "", attr_val)
    parsed_data.append(tmp_data)

  data_df = pd.DataFrame(parsed_data)
  return data_df

page = requests.get("https://scrapethissite.com/pages/forms/")
soup = BeautifulSoup(page.text, "html.parser")
pagination = soup.find("ul", attrs={"class": "pagination"})
link_elms = pagination.find_all("li")
links = [link_elm.find("a").attrs["href"] for link_elm in link_elms]
links = set(links)

temp_dfs = list()
for link in links:
  tmp_df = scrape_this(uri=link)
  temp_dfs.append(tmp_df)
hockey_team_df = pd.concat(temp_dfs, axis=0).reset_index()
hockey_team_df.sort_values(["year", "name"], inplace=True)

credentials_dict={  
  "type": "service_account",
  "project_id": "model-calling-343600",
  "private_key_id": "ac7eda61b6fa29bdcbe6ea02da2dd3f8ebaf450c",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCo1gzgUAt1Rosk\n2YzaTNKBcVRtXjHfoCSj/H3HvQKQoYzi3uCchClknBMnJG3JFcPv1HjAy3UPv89V\nCRxIbq7WKGa9NhgcVZemcs2cKb5/DgyZSTMmj4erAJ2XTw9IE92PSYK3IqtFYULQ\nlY8WDwP7VPqB0dYZ46w64nUkuiXxId30vsZqcvDBZUzA+VhNQJ6mBQ5M5WUyGcsG\nWmL/66GGAawOkkVuzHz3U3XmdodjwMQKnjwDtuRce1aicG4y58i8nBm+vbhbmfax\nLgM5VISvfEVSjQxGyi/FsqE1jpopbLYv0bsZYGNSWf3RuGLJmOu8s+E7oG2mzsUl\nnGSpHjZDAgMBAAECggEAA8EZJMz5QqcKONkMX6q3czQDPEvAA/V9kX0i8BPJxum/\nH/WNyan+RtbzoOCxMkUyIX1rhZOT0eeIsDh7vdHJDUkO5v3/cXRAllQImQR5A6R0\nokOO7oVHIoXPSBb0qe+LJmcF9mJZrAX6it6jtMoqFmbwceRdHh+o0kX72qoeMt6H\nj+TlWxfHyM6H8P8xTUKjlnLFe5pzXfOb+WQC3S9UX4WkzSC+cA6OxzSAp+PadrkH\nY9iCVotOdMV5hPZowHz/qBwNR/IaU9EN1H4Fr/2rUZk4NN95KIAK6yim7KOFtzbS\nlVnHxbEwUWOLtRiDBkVXdE/Jdr/e3UtiLD9JHPMIFQKBgQDbXqGpiGvh54pMsTSf\nPGYMBtp3qqbr2it9Hg5pxNPLRsJKEJKG9jXPQhgVrbK3SEZJ28PW1YCXrSgGvxq8\nNu4hGNoNRlTyKtN5aDaJ6bMnA82nmSC+vtH7sAXU8sh7DcDIkMJCD9OfGyy6FbPi\ndKEWHkwp5zBgZCTLbyaTn93rrQKBgQDFB0S3j1onE+krCuEBbnWyNX3445GfYAQH\no/b54al49WlheFxlos1gDUwfs08OEcPr6h1YS3Pw8A2t3Q7zlDMblCPBq+9yCt6e\nLewcm+4l/WDUaS6IYmTnMd/wBz/m8NrQcpr72BI8mrLguJa0pg/lfV9XUjxeNsxJ\n/MCEa+XnrwKBgQCaMRTupg42dlo2d+Ql/P05fOO4c0Hqy6n/ws2cuJWp7y2Hg8iK\nhqrh6HInYrUYsPt+1LL94YoGktZsj40KOI3+w4oZBJOWuFV2o7KaE6MyTDEUmcRz\nbosIHvyqZpBWNh+Imn+AkcFMt3wjvDd5eEL12gvs9CyDxEA8of76iscg7QKBgE2Z\ns0LovwUtHmTJgB1kOA7caqUgXDZ9RpkLxzZb3re5UKwHD70oBeOS2SyTHsvXy2ab\nartf3GZE5d5Ydo8RC6ANFJgu87vi9BMw2xHZiE6GISEH3D/zIPK9/gk3kb+PlV8M\nBGa0j1o3Q8SmbxTvYstsOaTWytgAlS1+0wRUytQZAoGBAMyliSLNBW8pi9/LXZgI\nxhRZvz8ENZPlYsKCTgvclcyLbj0d7iFnz5eNxUaiBD5hZtgqgq2/qGnFbHwaAYt9\nHVehzkxowTVWnspS/IJ0yNv6apzcqPWvZe7aWZSUvFeYw21fA37aIYSFfYPSHobX\ntfqepDfRZx7eJ4YWuhzV04je\n-----END PRIVATE KEY-----\n",
  "client_email": "storagedataops@model-calling-343600.iam.gserviceaccount.com",
  "client_id": "104637843235005142622",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/storagedataops%40model-calling-343600.iam.gserviceaccount.com"

}
credentials =service_account.Credentials.from_service_account_info(credentials_dict)
storage_client = storage.Client(credentials=credentials)
bucket = storage_client.get_bucket('atividade4_dataops_names')
blob = bucket.blob('hockey.sql')

hockey_team_df.to_sql("hockey",con=engine,if_exists="replace",index=False)
data_sql=hockey_team_df.astype(str)
data_sql_str=data_sql.to_string(index=False)
blob.upload_from_string(data_sql_str.encode('utf-8'),content_type="application/sql")