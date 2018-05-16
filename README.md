You must change database settings in settings.py.

s = requests.Session()

s.auth = (‘superusername’, ‘password’)

————————————————————————————————————————————————————————————————————————

library_url='http://127.0.0.1:8000/library'

book_url='http://127.0.0.1:8000/book/’

author_url='http://127.0.0.1:8000/author/’

book_id_url='http://127.0.0.1:8000/book/id’

author_id_url='http://127.0.0.1:8000/author/id’


————————————————————————————————————————————————————————————————————————

/library/

files = {'upload_file': open(‘file path’,’r’)}

Bu sekilde cursor sonda kaliyor tekrar file gondermek icin cursoru en basa guncelleyin
dosya =files.get('upload_file')
 
dosya.seek(0,0)


——————————————————————————————————————————————————————————————————————————

/library/

Library post and patch request.

POST: CSV file, in the body, removes everything from the database and creates a new one with all books ands authors from the database.

PATCH: CSV file, in the body, adding just these books, with the author.

r = s.post(library_url, files=files)

r = s.patch(library_url, files=files)


——————————————————————————————————————————————————————————————————————————————————

/book/

Book get, post request

GET: List of books. Can be filtered with a regex “filter” parameter from the query string

POST: New book

To doing regex search you have to add query into url or add params in get request

r = s.get(book_url)

r = s.get(book_url,params={})

In order to create new book, you have to post request with lc_classification,title,authors fields. authors field must be like that authors = name,surname,birth_date. birth_date field must be YYYY-MM-DD format(ex. 2000-10-03)

r = s.post(book_url, body=params)

r = s.post(book_url, body=params)


——————————————————————————————————————————————————————————————————————————————————

/author/

Author get, post request

GET: List of authors. Can be filtered with a regex “filter” parameter from the query string

POST: New book

To doing regex search you have to add query into url or add params in get request

r = s.get(book_url)

r = s.get(book_url,params={})

In order to create new author, you have to post request with name,surname,books fields. books field must be like that books=title,lc_classification. birth_date field must be YYYY-MM-DD format(ex. 2000-10-03)

r = s.post(book_url, body=params)

—————————————————————————————————————————————————————————————————————————————————

/book/{id}/

GET: Book details

PATCH: Update this book with a set of details

PUT: Replace all fields of this book
************************************************************

Get request

r = s.get(book_id_url)

******************************************************

Put request

headers = {‘Content-Type’:’xapplication/x-www-form-urlencoded’

r = s.put(book_id_url,headers=headers, body=params)

Params have to contain minimum 3 fields(title,lc_classification,authors)
If you want add more than one author, you should add new authors field when invoke patch function. authors field must be like that authors = name,surname,birth_date. birth_date field must be YYYY-MM-DD format(ex. 2000-10-03)


************************************************************

Patch request

headers = {‘Content-Type’:’xapplication/x-www-form-urlencoded’

r = s.patch(book_id_url,headers=headers, body=params)

you have to add field which you want update to params
When you add authors to book, authors field must be like that authors = name,surname,birth_date. birth_date field must be YYYY-MM-DD format(ex. 2000-10-03)

————————————————————————————————————————————————————————————————————————————————————————

/author/{id}/

GET: Author details

PATCH: Update this author with a set of details

PUT: Replace all fields of this author

************************************************************

Get request

r = s.get(author_id_url)

******************************************************

Put request

headers = {‘Content-Type’:’xapplication/x-www-form-urlencoded’

r = s.put(author_id_url,headers=headers, body=params)

Params have to contain minimum 4 fields(name,surname,birth_date,books)
If you want add more than one book, you should add new authors field to params when invoke patch function .

************************************************************

Patch request


headers = {‘Content-Type’:’xapplication/x-www-form-urlencoded’

r = s.patch(author_id_url, headers=headers, body=params)

you have to add field which you want update to params
When you add books to author, books field must be like that books = title,lc_classification.

————————————————————————————————————————————————————————————————————————————————————————