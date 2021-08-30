from bs4 import BeautifulSoup
import requests
import os, os.path, csv

# get the link of all categories article in vnexpress
def get_link_of_categories (soup, link):
    unvisited_link = []
    categories = []
    for _ in soup.find_all('option'):
        tmp = str(link) + str(_.get('value'))
        unvisited_link.append(tmp)
        categories.append (_.get_text())
    return unvisited_link, categories

def get_link_of_content(soup):   
    # get the link of all ariticles in a page of website 
    link_content = [] 
    for i in soup.find_all('h3', {'class':'title-news'}):
        for j in i:
            link_content.append (j['href'])
    return link_content


# get next page of website
def get_link_next_page (soup, link):
    for i in soup.find_all ('a', {'class':'btn-page next-page'}):
        next_page = i['href']
        return link + next_page
    return 0

# # get the time and title of a content
# def get_title_time_of_content (soup):
#     for i in soup.find_all ('h1', {'class':'title-detail'}):
#         title = i.text
#     for i in soup.find_all ('span', {'class':'date'}):
#         time = i.text
#     return title, time

def main():
    with open('result.csv', 'a', encoding='utf-8') as file:
        fieldnames = ['Title', 'Time', 'Categories']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # use request lib to "communicate" with the sever
        _request = requests.get('https://vnexpress.net/category/day?cateid=1001005&fromdate=1597536000&todate=1600214400&allcate=1001005')
        # transmission the result of the request.get to BeautifulSoup
        soup = BeautifulSoup(_request.text, 'html.parser')
        link = 'https://vnexpress.net'
        # unvisite_link is a variable to store the list of link of categories such as Thời Sự, Thể Thao
        unvisited_link, categories = get_link_of_categories(soup, link)
        # loop over the link in unvisited link
        for link, _categories in zip (unvisited_link, categories):
            # get HTML of a the frist page in each categories
            _request_of_categories = requests.get(link)
            soup_catagories = BeautifulSoup (_request_of_categories.text, 'html.parser')
            # count variable to check the first page in any categories
            count = 1
            # current_html_page to store the current page
            current_html_page = soup_catagories
            link_next_page = 1
            # loop over all page in categories
            while link_next_page != 0:
                # if the first time it will crawl in the frist page
                print (count)
                if (count == 1):
                    # link_content is a variable to store all the link in a page
                    link_content = get_link_of_content (current_html_page)
                # from the second time it will crawl the html of next page until it cant find any page
                else:
                    link_next_page = get_link_next_page(current_html_page, link)
                    # if dont have any next page, we will break the loop and go to next categories
                    if (link_next_page == 0):
                        break
                    _request_of_link_content_next_page = requests.get(link_next_page)
                    soup_content_next_page = BeautifulSoup (_request_of_link_content_next_page.text, 'html.parser')
                    current_html_page = soup_content_next_page
                    link_content = get_link_of_content (current_html_page)
                for _link_content in link_content:
                    _request_of_link_content = requests.get(_link_content)
                    soup_content = BeautifulSoup (_request_of_link_content.text, 'html.parser')
                    # Crawl the title and time of the content
                    for k in soup_content.find_all ('h1', {'class':'title-detail'}):
                        title = k.text
                    for n in soup_content.find_all ('span', {'class':'date'}):
                        time = n.text
                    writer.writerow ({'Title': title, 'Time':time, 'Categories': _categories})
                    # remove the link we approved in link_content
                    link_content.remove(_link_content)
                    # if dont have any link in list link_content we will break the loop and go to the next page 
                    if (len (link_content) == 0):
                        break
                
                count += 1

main()


