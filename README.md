# Proposal

## What will (likely) be the title of your project?

PSet Party

## In just a sentence or two, summarize your project. (E.g., "A website that lets you buy and sell stocks.")

Website for students in a class to connect with one another so that they can find times to work together.

## In a paragraph or more, detail your project. What will your software do? What features will it have? How will it be executed?

Through our website, we hope to make it easier for students to work together on problem sets and projects. The first time that users visit the website, they will be prompted to make an account through the registration page. After registering, they can log in with their password and username to be redirected to a homepage where they can add classes and view the classes that they are currently taking. When users click on a specific class, they will be redirected to the class page, which displays a sorted table of other students in the class, along with the times that they are planning to work. Users can update the times that they are available through a form accessible from the class page, and they can also view the contact information of other users by clicking on their name.

We plan to implement the project by using SQL to handle databases, Python and HTML to create a dynamic website, and Bootstrap to create nice graphics.

## If planning to combine CS50's final project with another course's final project, with which other course? And which aspect(s) of your proposed project would relate to CS50, and which aspect(s) would relate to the other course?

N/A

## In the world of software, most everything takes longer to implement than you expect. And so it's not uncommon to accomplish less in a fixed amount of time than you hope.

### In a sentence (or list of features), define a GOOD outcome for your final project. I.e., what WILL you accomplish no matter what?

- Registration page
- Login page
- “Add classes” page
    - List current classes
    - Dropdown list of a few (15ish?) classes
- Time update page
    - Redirected from specific class homepage
    - Update available times for the coming 7 days
- Home page that displays all classes
- Class Homepage
    - Current students
    - List out times available (sorted by most recent day)
- User Homepage
    - Contact details (for them to manually email)
    - View all classes they are taking

### In a sentence (or list of features), define a BETTER outcome for your final project. I.e., what do you THINK you can accomplish before the final project's deadline?
** = new functionality
- Registration page
- Login page
- “Add classes” page
    - List current classes
    - Drop down list of which department, then user inputs course number**
- Time update page
    - Redirected from specific class homepage
    - Update available times for the coming 7 days
- Home page that displays all classes
- Class Homepage
    - Current students
    - List out times available by day
        - Update the page each day: Remove days that have already passed and
      add upcoming days so that users can always see a full week ahead**
        - Location: Students can indicate where they’re working**
        - Green dot indicator: If user presses a button that indicates they’re psetting now,
      a green dot will appear next to their name; they can also press a button to remove
      the green dot**
- User Homepage
    - Contact details
    - View all classes they are taking
    - Email functionality (directly through website)**
- Fancier graphics**
- Navigation bar**
- Ability to edit and remove list of classes/available times**

### In a sentence (or list of features), define a BEST outcome for your final project. I.e., what do you HOPE to accomplish before the final project's deadline?
** = new functionality
- Registration page
- Login page
- “Add classes” page
    - List current classes
    - Drop down list of which department, then user inputs course number**
- Time update page
    - Redirected from specific class homepage
    - Update available times for the coming 7 days
- Home page that displays all classes
- Class Homepage
    - Current students
    - List out times available by day
        - Update the page each day: Remove days that have already passed and add upcoming days so that users can always see a full week ahead**
        - Location: Students can indicate where they’re working**
        - Green dot indicator: If user presses a button that indicates they’re psetting now, a green dot will appear next to their name; they can also press a button to remove the green dot**
        - Groups:**
            - Function to create a group
            - Function to join a group
            - Function to disband group (?)
        - List of past students who’ve taken the classes and are willing to help**
- User Homepage
    - Contact details
    - View all classes they are taking
    - Email functionality (directly through website)**
- Fancier graphics**
- Navigation bar**
- Ability to edit and remove list of classes/available times**

## In a paragraph or more, outline your next steps. What new skills will you need to acquire? What topics will you need to research? If working with one of two classmates, who will do what?

14 Nov to 25 Nov:
- Work on and achieve the “Good” target of the project
- According to allocations below

Alden:
- Login, Registration
- Generating user homepage
- Search class page with search bar function
- Create Databases

Mirilla:
- Create class homepage, along with calendar and student pages
- Create time update form
- Edit functionality for available times

Tat Wei:
- Create function for shuffling the time update table based on day of the week
- Prevent old entries from showing
- Email Functionality
- “Pset Now!” button and Green Dot function

25 Nov:
- Team Meeting to update each other on progress and discuss the way forward
- Work on Status Update

26 Nov to 2 Dec:
- Debug previous week’s work
- Implement “better” outcome
- Develop graphics
- Consider corner cases

Skills and Languages Needed:
- Python
- HTML, CSS, Bootstrap
- Javascript
- SQLite data manipulation
- Email functionality
