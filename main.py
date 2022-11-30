from bs4 import BeautifulSoup
import urllib3
import json
from flask import Flask, render_template, request, redirect, url_for

def scrape(url):
  "create json file from web scraping 'url' "
  # initiate a 'get' request to the given 'url' with urllib3 objects
  http = urllib3.PoolManager()
  requested = http.request('GET', url)
  # 'url_soup' is a beautiful soup object that we'll
  # use to filter through the html in the corresponding webpage
  # of the address 'url'
  url_soup = BeautifulSoup(requested.data.decode('utf-8'), "html5lib")
  # 'data' is a list that will contain all the data we wish to
  # convert into a json file after completion of web scraping
  data = []
  # 'nameTags' is a beautiful soup object that contains
  # the html tags which hold the names of the MSCS faculty
  nameTags = url_soup.find_all('span', attrs={'class': '_name'})
  # iterate over the html tags with 'tag' as an item
  # in 'nameTags'
  for tag in nameTags:
    # we save the text inside the html tag into a list
    # because the names are in the format of '[last name], [first name]'
    # and i wish to save the names of the MSCS faculty as just
    # '[first name] [last name]' 
    name_list = tag.text.split()
    # 'new_name' will contain the name of a MSCS faculty member
    # in the format desired after completing some operations on             # 'new_list'
    new_name = ""
    # after enumerating over 'new_list', we have access to the index
    # of an item in 'new_list' hence the var name, 'idx', and a partial     # name of the faculty member hence the var name, 'name'
    for idx, name in enumerate(name_list):
      # if a ',' is not found in 'name' then
      # we'll add 'name' to 'new_name' and then
      # after all the partial names are added to 'new_name'
      # we can add the partial name that has a ',' by saving the index
      # of that entry
      if ',' in name:
        comma_index = idx
      else:
        # add appropriate spacing
        new_name += name + " "
    # add the remaining entry but remove the comma before
    # adding it to 'new_name' using string splicing
    new_name += name_list[comma_index][:-1]
    # we have the faculty members name in first name last name format
    # so we can append the name to 'data'
    data.append([new_name])
  # 'emailTags' is a beautiful soup object that contains
  # the html tags which hold the emails of the MSCS faculty
  emailTags = url_soup.find_all('span', attrs={'class': '_email'})
  # we can use the index of each iteration as a way to
  # access the corresponding list in 'data' to a specific MSCS faculty
  # member as the order of retrieving these emails matches the same order
  # as the lists in 'data'
  for idx, tag in enumerate(emailTags):
    # 'tag.text.strip()' is the faculty member email with whitespace removed
    # and then we add that email to the corresponding faculty member's list
    # of information in 'data'
    data[idx].append(tag.text.strip())
  # 'info_field' is a beautiful soup object that contains
  # the html tags which contain the anchor tags that we'll
  # use to retrieve the urls of the homepages of the faculty
  info_field = url_soup.find_all('div', attrs={'class': '_colA'})
  # there are multiple instances of the class '_colA' and this is a div
  # tag so we can think of an item from 'info_field' as a div tag hence
  # var name 'div' and we can once again add information into 'data' for
  # corresponding faculty by index in each iteration
  for idx, div in enumerate(info_field):
    # 'homepg_url' is the url of a faculty member after retrieving
    # the url from an anchor tag
    homepg_url = div.find('a')['href']
    # we want to web scrape each faculty member's homepage so we need
    # to make a 'GET' request and create a beautiful soup object to filer
    # the html for each webpage
    homepg_requested = http.request('GET', homepg_url)
    homepg_soup = BeautifulSoup(homepg_requested.data.decode('utf-8'),
                                "html5lib")
    # 'homepg_field' is a beautiful soup object that contains
    # the html tags which contain the schedules of the MSCS
    # faculty
    homepg_field = homepg_soup.find_all('div', attrs={'class': 'u-rich-text'})
    # theres multiple instances of the 'u-rich-text' class in each
    # webpage so we can filter through them by a for loop and since
    # these are div tags, the var name is 'inside_div'
    for inside_div in homepg_field:
      # the '_content' attribute comes up in the instances of the
      # div class where the schedule of the faculty member is not mentioned
      # so we want to look at all the other div tags
      if "_content" not in str(div):
        try:
          # we'll create a list to contain the times where a member
          # is teaching
          schedules = []
          # 'content' is a variable containing the time ranges
          # of when a faculty member teaches and we can split
          # this string into a list to remove whitespace and properly
          # save the schedule of the faculty member
          content = inside_div.find('ul').text.split()
          # iterate over 'content'
          for element in content:
            # when '-' is in the item of 'content' then we want to append
            # that item as that will allow us to create a list of the                   # different times a faculty member is teaching with each
            # item following the format XX:XX:XX-YY:YY:YY where the X's
            # and Y's are obviously replaced by some numbers to give 
            # a 24-hour time format range
            if '-' in element:
              schedules.append(element)
        # it's possible a faculty member doesnt have a teaching schedule
        except AttributeError:
          schedules = []
    # we have retrieved the schedule of the faculty member
    # and we can now save their schedule and page url by index
    data[idx].append(schedules)
    data[idx].append(homepg_url)
    
  # we have finished web scraping and saving to 'data' and
    # we can now write and close to a json file by dumping
    # 'data' to that file
  json_writer = open("faculty.json", "w")
  json.dump(data, json_writer, indent=1)
  json_writer.close()


def run_app():
  "start server for webpage and run flask backend logic"

  # retrieve json data in  the form of a list to access
  # for webpage functionality
  data = json.load(open("faculty.json", "r"))
  
  # create flask object for decorators
  app = Flask(__name__)

  
  @app.route('/')
  def index():
    "return root page"
    return render_template('index.html')

  @app.route('/faculty', methods=['GET', 'POST'])
  def faculty():
    "handle form submission from root page"
    # the user clicked the 'Search' button in the root page
    if request.method == 'POST':
      # retrieve any possible inputs for
      # an email or time of teaching from the form submitted
      given_email = request.form['email']
      given_time = request.form['time']
      # redirect the user to a url based on what
      # kind of input they gave
      if given_email:
        return redirect(url_for('email_search', email=given_email))
      elif given_time:
        return redirect(url_for('time_search', time=given_time))
      else:
        # the user didnt supply any inputs
        return render_template("index.html", faculty_info="No Results")
    else:
      # a "GET" request is triggered
      return redirect(url_for('faculty'))

  @app.route('/time_search/<time>', methods=['GET', 'POST'])
  def time_search(time):
    "display faculty that teach in the timeframe given"
    # Note the user should enter time in standard 12 hour
    # time format so 12pm is allowed and so is 12:30pm,
    # 11am, 11:30am, etc.

    # the first part of this function handles converting
    # 'time' from 12 hour format to 24 hour format
    # and then after that process we render the webpage
    # with the desired content
  
    
    # redirecting to the url '/time_search/<time>' will
    # trigger a 'GET' request
    if request.method == 'GET':
      # 'time_period' should be either 'am' or 'pm' and we
      # retrieve this with string slicing with 'time' which
      # is the users input of teaching times for faculty
      time_period = time[-2:]
      # after retrieving the time period we split
      # the problem into two cases, the case of the time period
      # being 'am' and the case of the time period being 'pm'

      
      if time_period == 'am':
        # the user has inputed a time with a minutes value if
        # ':' is in 'time' so we handle that case
        if ':' in time:
          # we can iterate over the characters of 'time'
          # and save the indexes of ':' and 'a' as these
          # will be the separators between the string slices
          # we want to retrieve hence the var names 'sep_index_one'
          # and 'sep_index_two' 
          for idx, char in enumerate(time):
            if char == ":":
              sep_index_one = idx
            elif char == 'a':
              sep_index_two = idx
          # the hours and the mins in 'time' can now be retrieved 
          # by string slicing
          hours = time[:sep_index_one]
          mins = time[sep_index_one + 1:sep_index_two]

          # if 'hours' < 10 that means a 'hours'
          # should be followed by a '0' but if 'hours' is >= 10
          # then we shouldnt have 'hours' be followed by a '0'
          
          # note in all the following conditionals, we save
          # the converted 24 hour version of 'time' to the variable
          # 'new_time'
          if int(hours) < 10:
            # same thing with 'mins' when it comes to adding a '0'
            # like the situation with 'hours'
            if int(mins) < 10:
              new_time = "0" + hours + ":0" + mins + ":00"
            else:
              new_time = "0" + hours + ":" + mins + ":00"
          else:
            # now 'hours' >= 10
            
            # we can handle the special case of when the user
            # inputs 12:50am by setting 'hours' = '00'
            if int(hours) == 12:
              hours = "00"
              
            # handle formatting 'mins' in this case with
            # appropriate guidelines
            if int(mins) < 10:
              new_time = hours + ":0" + mins + ":00"
            else:
              new_time = hours + ":" + mins + ":00"
        else:
          # the user inputed just a hours time like 12pm,1pm,10am,etc.
          # we retrieve 'hours' by string formatting
          hours = time[:-2]
          # we format 'hours' like the cases above but with specific
          # guidelines to this case
          if int(hours) < 10:
            new_time = "0" + hours + ":00:00"
          else:
            # handle the case of '12am'
            if int(hours) == 12:
              hours = "00"
            new_time = hours + ":00:00"

      elif time_period == 'pm':
        # the user has inputed a time with a minutes value if
        # ':' is in 'time' so we handle that case
        if ':' in time:
          # we can iterate over the characters of 'time'
          # and save the indexes of ':' and 'a' as these
          # will be the separators between the string slices
          # we want to retrieve hence the var names 'sep_index_one'
          # and 'sep_index_two' 
          for idx, char in enumerate(time):
            if char == ":":
              sep_index_one = idx
            elif char == 'p':
              sep_index_two = idx
          # the hours and the mins in 'time' can now be retrieved 
          # by string slicing
          hours = time[:sep_index_one]
          mins = time[sep_index_one + 1:sep_index_two]
          # since we're working with 'pm' times now in all cases besides
          # when the hours value is 12 like 12pm, 12:30pm, we can compute
          # the new 24 hour format hour value by adding 12 to the hour value
          # we do that in this conditional to reassign 'hours'
          if int(hours) != 12:
            hours = str(int(hours) + 12)
          # we once again handle the cases of the minutes value
          # by adding appropriate formatting based off the digits of
          # the number
          if int(mins) < 10:
            new_time = hours + ":0" + mins + ":00"
          else:
            new_time = hours + ":" + mins + ":00"
        else:
          # the user didn't input a time with a minutes value
          hours = time[:-2]
          # we convert the 12 hour time to a 24 hour time
          if int(hours) != 12:
            hours = str(int(hours) + 12)
          new_time = hours + ":00:00"
      # we have now converted the 12 hour time to 24 hour time

      # 'li_names' is a variable that will look through the information
      # stored in 'data' and add on html tags to itself with the content
      # inside those html tags being the names of the faculty members
          
      # we can make our website render the html inside 'li_names' by
      # the jinja key word '|safe' located inside 'index.html'

      # we're adding li tags to 'li_names' with the content being faculty
      # names hence the var name 'li_names'
      li_names = ""
      # 'point' is a list object that matches the following format
      # here, [name, email, [time range, time range, ...], website url]
      # so we can use indexing on 'point' to get the data we want
      for point in data:
        # point[2] is a list containing the time ranges of when a 
        # faculty member is teaching
        for time_range in point[2]:
          # check if 'new_time' is in one of the time ranges for a match
          if new_time in time_range:
            # there is a match with the users input and the faculty's
            # schedule so we add on the faculty's member name and we also
            # issue an anchor tag so the user will be able to click
            # on the li tag content and be sent to the faculty member's
            # homepage and we do this by using indexes with 'point'
            li_names += '<li><a href={}>'.format(point[3]) + point[0] + '</a></li>'
            # we dont want to have a faculty member's name appear
            # twice in case theres multiple times in the week they
            # teach during the inputed time
            # so we do 'break' to prevent that unwanted behavior
            break
      # 'usr_input' is a string that we'll render into the html
      # to remind the user what input they gave
      usr_input = 'Time Searched: "{}"'.format(time)

      # we can now render the html with the variables
      # to produce the results of the time search
      return render_template('index.html', user_input = usr_input,faculty_info=li_names)

  @app.route('/email_search/<email>', methods=['GET', 'POST'])
  def email_search(email):
    """Display faculty member names if the inputed 'email' value is  
    a substring of a faculty member's email"""

    # a 'GET' request is issued when the user is redirected
    # to the url '/email_search/<email>'
    if request.method == 'GET':
      # 'li_names' is a variable that will look through the information
      # stored in 'data' and add on html tags to itself with the content
      # inside those html tags being the names of the faculty members
      
      # we can make our website render the html inside 'li_names' by
      # the jinja key word '|safe' located inside 'index.html'
      li_names = ""
      # 'point' is a list object that matches the following format
      # here, [name, email, [time range, time range, ...], website url]
      # so we can use indexing on 'point' to get the data we want
      for point in data:
        # 'is_sub_string' stores a boolean value that we'll use
        # to see if 'email' is a substring of a faculty member's email
        # after an iterative process checking to see if the elements
        # in 'email' match the elements of 'faculty_email'
        is_sub_string = True
        faculty_email = point[1]
        # if 'email' is a longer string than 'faculty_email'
        # then its impossible for 'email' to be a substring
        # of 'faculty_email'
        if len(email) > len(faculty_email):
          is_sub_string = False
        else:
        # we can use range(len(email)) to check
        # if each character of 'email' matches with 'faculty_email'
        # by index
          for idx in range(len(email)):
            if email[idx] != faculty_email[idx]:
              is_sub_string = False
        # after the iterative process if 'is_sub_string' == True
        # then 'email' is indeed a substring of the corresponding
        # faculty member's email and we will add on the faculty's member            # name and we also
        # issue an anchor tag so the user will be able to click
        # on the li tag content and be sent to the faculty member's
        # homepage and we do this by using indexes with 'point'
        if is_sub_string:
          li_names += '<li><a href={}>'.format(point[3]) + point[0] + '</a></li>'
      # 'usr_input' is a string that we'll render into the html
      # to remind the user what input they gave
      usr_input = 'Email Searched: "{}"'.format(email)
      # we can now render the html with the variables
      # to produce the results of the time search
      return render_template("index.html", user_input = usr_input, faculty_info=li_names)

  # we must run the method 'app.run()' to start the server for the
  # the webpage to run
  app.run(host='0.0.0.0', port=81)

# call 'run_app()' to start the web app
run_app()
