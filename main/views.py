# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpResponse
from models import AuthorMod, Book as BookMod
import csv
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import StringIO
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
import operator
import unicodedata
import urllib

@csrf_exempt
def library(request):
    if request.method == 'POST':
        try:
            BookMod.objects.all().delete()
            AuthorMod.objects.all().delete()
        except:
            pass

        paramfile = request.FILES['upload_file']

        if read_from_csv(paramfile):
            return JsonResponse(
                {'result': 'Csv file has saved to database', 'status_code': 200})
        else:
            return JsonResponse({'result': 'Error occured when try to save data',
                                 'status_code': 500})

    elif request.method == 'PATCH':

        paramfile = body_parser(request.body)

        if read_from_csv(paramfile):
            return JsonResponse(
                {'result': 'Data has saved to database', 'status_code': 200})
        else:
            return JsonResponse({'result': 'Error occured when try to save data',
                                  'status_code': 500})

    else:
        return HttpResponse('GETREQ')






@method_decorator(csrf_exempt, name='dispatch')
class Book(View):
    def get(self, request, book_id=None):
        if book_id:
            book = check_book_id(book_id)
            if type(book) == JsonResponse:
                return book


            return JsonResponse({'Book Title': book.title,
                                     'Book Lc_Classification':
                                         book.lc_classification,
                                     'Book Authors':
                                         [(auth.name, auth.surname)
                                          for auth in book.authors.all()]
                })

        else:
            filter_params = ('title', 'lc_classification', 'authors__name')
            my_dict = json.loads(json.dumps(request.GET))
            if len(my_dict) == 0:
                result = list(AuthorMod.objects.values())
                return JsonResponse({'result': result, 'status_code': '200'})
            my_dict['authors__name'] = my_dict.get('authors')
            result = get_filter(filter_params=filter_params,
                                query_strings=my_dict, model_name='book')


        return JsonResponse({'result': result, 'status_code':200})

    def post(self, request, *args, **kwargs):
        authors = request.POST.getlist('authors')
        title = request.POST.get('title')
        lc_classification = request.POST.get('lc_classification')
        if not BookMod.objects.filter(title=title,
                                      lc_classification=lc_classification).exists():
            book_obj = BookMod.objects.create(title=title,
                                              lc_classification=lc_classification)
        else:
            return JsonResponse({'Messages': 'Book already exists on database',

                             'Status Code': '400'})
        for index in range(len(authors)):
            author_list = (authors[index]).split(',')
            auth_filter = AuthorMod.objects.filter(name=author_list[0], surname=author_list[1], birth_date=author_list[2])

            if not auth_filter:
                auth_obj = AuthorMod.objects.create(name=author_list[0], surname=author_list[1], birth_date=author_list[2])
                book_obj.authors.add(auth_obj)
            else:
                book_obj.authors.add(auth_filter)

        return JsonResponse({'result': 'Created new book', 'status_code': 200})


    def patch(self,request, book_id):
        if book_id:

            book_obj = check_author_id(book_id)
            if type(book_obj) == JsonResponse:
                return book_obj
            result = extract_data_from_patch_or_put_body(request.body)
            set_patch_book_obj(book_obj, result)
            # for item in request.body.split('&'):
            #     key_value = urllib.unquote(item).split('=')
            #     if key_value[0] in result:
            #         result[key_value[0]] += [key_value[1]]
            #     else:
            #         result[key_value[0]] = [key_value[1]]
                # try:
                #     data = str(result[urllib.unquote(urllib.unquote(item)).split('=')[0]]) + ',' + str(urllib.unquote(urllib.unquote(item)).split('=')[1])
                # except KeyError:
                #     data += str(urllib.unquote(urllib.unquote(item)).split('=')[1])
                #
                # result[str(urllib.unquote(urllib.unquote(item)).split('=')[0])] = data
                # data = ''

            return JsonResponse({'Message': 'Book Object Changed',
                                 'Status_Code': '200'})

    def put(self, request, book_id):
        if book_id:
            book_obj = check_author_id(book_id)
            result = extract_data_from_patch_or_put_body(request.body)
            if len(result) < 3:
                return JsonResponse({'Message': 'Wrong Param',
                                     'Status_code': '404'})
            else:
                set_put_book_obj(book_obj, result, pk=book_id)

        return JsonResponse({'Message': 'Book Object Changed',
                             'Status_Code': '200'})


@method_decorator(csrf_exempt, name='dispatch')
class Author(View):
    def get(self, request, author_id=None):
        if author_id:
            author_obj = check_author_id(author_id)
            if type(author_obj) == JsonResponse:
                return author_obj


            return JsonResponse({'Author Name': author_obj.name,'Author Surname':author_obj.surname,
                                     'Book Lc_Classification':
                                         author_obj.surname,
                                     "Author's Book":
                                         [(book.title, book.lc_classification)
                                          for book in author_obj.books.all()]
                })

        else:

            filter_params = ('name', 'surname', 'birth_date', 'books__title')
            my_dict = json.loads(json.dumps(request.GET))
            if len(my_dict) == 0:
                result = list(AuthorMod.objects.values())
                return JsonResponse({'result': result, 'status_code': '200'})

            my_dict['books__title'] = my_dict.get('books')
            result = get_filter(filter_params=filter_params,
                                query_strings=my_dict, model_name='author')

        return JsonResponse({'result': result, 'status_code': 200})


    def post(self, request):
        books = request.POST.getlist('books')
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        birth_date = request.POST.get('birth_date')
        if not AuthorMod.objects.filter(name=name,
                                        surname=surname,birth_date=birth_date).exists():
            author_obj = AuthorMod.objects.create(name=name,
                                                  surname=surname,
                                                  birth_date=birth_date)
        else:
            return JsonResponse({'Messages': 'Author already exists on database',
                                 'Status Code': '400'})
        for index in range(len(books)):
            book_list = (books[index]).split(',')
            book_filter = BookMod.objects.filter(title=book_list[0],
                                                 lc_classification=book_list[1],
                                                   )

            if not book_filter:
                book_obj = BookMod.objects.create(title=book_list[0],
                                                  lc_classification=book_list[1])
                author_obj.books.add(book_obj)
            else:
                author_obj.books.add(*book_filter)

        return JsonResponse({'result': 'Created new author', 'status_code': 200})

    def put(self, request, author_id=None):
        if author_id:

            author_obj = check_author_id(author_id)

            if type(author_obj) == JsonResponse:
                return author_obj
            result = extract_data_from_patch_or_put_body(request.body)
            if len(result) < 4:
                return JsonResponse({'Message': 'Wrong Param',
                                     'Status_code': '404'})
            else:
                set_put_auth_obj(author_obj, result, pk=author_id)

        return JsonResponse({'Message': 'Author Object Changed',
                             'Status_Code': '200'})

    def patch(self, request, author_id):
        if author_id:
            author_obj = check_author_id(author_id)
            if type(author_obj) == JsonResponse:
                return author_obj
            result = extract_data_from_patch_or_put_body(request.body)
            set_patch_auth_obj(author_obj, result)

        return JsonResponse({'Message': 'Author Object Changed',
                             'Status_Code': '200'})

def read_from_csv(file):
    spramreader = csv.reader(file, delimiter=",", quotechar='"')

    for row in spramreader:
        my_authors = []
        # try:
        if not BookMod.objects.filter(
                title=row[0],
                lc_classification=row[1]).exists():
            book_obj = BookMod.objects.create(title=row[0],
                                          lc_classification=row[1])

            author_list = row[2:]

            for item in range(len(author_list) / 3):
                author_birth_date = author_list.pop()
                author_surname = author_list.pop()
                author_name = author_list.pop()
                my_auth = AuthorMod.objects.filter(
                        name=author_name,
                        surname=author_surname, birth_date=author_birth_date)

                if not my_auth:
                    my_authors.append(
                    AuthorMod.objects.create(name=author_name, surname=author_surname,
                                          birth_date=author_birth_date))
                else:
                    my_authors.append(my_auth[0])
                # except:
                # pass

            book_obj.authors.add(*my_authors)
    return True


def body_parser(request_body):
    request_body = request_body.split('text/csv')[1].split('--')[0].strip()
    return StringIO.StringIO(request_body)

def extract_data_from_patch_or_put_body(request_body):
    result = {}
    for item in request_body.split('&'):
        key_value = urllib.unquote(item).split('=')
        if key_value[0] in result:
            result[key_value[0]] += [key_value[1]]
        else:
            result[key_value[0]] = [key_value[1]]

    return result

def set_patch_book_obj(book_obj, result):
    for key, value in result.items():
        if key == 'authors':
            book_obj.authors.clear()

            for item in value:
                auth_list = item.split(',')
                auth_obj = AuthorMod.objects.filter(name=auth_list[0],
                                                 surname=auth_list[1],
                                                 birth_date=auth_list[2])
                if not auth_obj:
                    new_auth_obj = AuthorMod.objects.create(name=auth_list[0],
                                                         surname=auth_list[1],
                                                         birth_date=auth_list[
                                                             2])

                    book_obj.authors.add(new_auth_obj)
                else:
                    book_obj.authors.add(auth_obj[0])

        else:
            setattr(book_obj, key, value[0])

    book_obj.save()

def set_patch_auth_obj(auth_obj, result):
    for key, value in result.items():
        if key == 'books':
            auth_obj.books.clear()

            for item in value:
                book_list = item.split(',')
                book_obj = BookMod.objects.filter(title=book_list[0],
                                                  lc_classification=book_list[1])
                if not book_obj:
                    new_book_obj = BookMod.objects.create(title=book_list[0],
                                                          lc_classification=book_list[1])

                    auth_obj.books.add(new_book_obj)
                else:
                    auth_obj.books.add(book_obj[0])

        else:
            setattr(auth_obj, key, value[0])

    auth_obj.save()

def set_put_book_obj(book_obj, result,pk):
    book_obj_list = []
    field_dict = {}
    for key, value in result.items():
        if key == 'authors':
            book_obj.authors.clear()

            for item in value:
                auth_list = item.split(',')
                auth_obj = AuthorMod.objects.filter(name=auth_list[0],
                                                 surname=auth_list[1],
                                                 birth_date=auth_list[2])
                if not auth_obj:
                    new_auth_obj = AuthorMod.objects.create(name=auth_list[0],
                                                         surname=auth_list[1],
                                                         birth_date=auth_list[
                                                             2])

                    book_obj_list.append(new_auth_obj)
                else:
                    book_obj_list.append(auth_obj[0])

        else:
            field_dict[key] = value[0]

    book_obj.authors.add(*book_obj_list)
    BookMod.objects.filter(pk=pk).update(**field_dict)

def set_put_auth_obj(auth_obj, result,pk):
    auth_obj_list = []
    field_dict = {}
    for key, value in result.items():
        if key == 'books':
            auth_obj.books.clear()

            for item in value:
                book_list = item.split(',')
                book_obj = BookMod.objects.filter(title=book_list[0],
                                                  lc_classification=book_list[1])
                if not book_obj:
                    new_book_obj = BookMod.objects.create(title=book_list[0],
                                                          lc_classification=book_list[1])

                    auth_obj_list.append(new_book_obj)
                else:
                    auth_obj_list.append(book_obj[0])

        else:
            field_dict[key] = value[0]

    auth_obj.books.add(*auth_obj_list)
    AuthorMod.objects.filter(pk=pk).update(**field_dict)

def get_filter(filter_params,query_strings,model_name):
    obj_dict = {}
    result = {}

    # query_strings['authors__name'] = query_strings.get('authors')
    # query_strings['books__name'] = query_strings.get('books')


    filter_clauses = [
        Q(**{'{0}__{1}'.format(filter_name, 'icontains'): query_strings.get(filter_name)})
        for filter_name in filter_params
        if query_strings.get(filter_name)]

    if filter_clauses and model_name == 'book':
        queryset = BookMod.objects.filter(
            reduce(operator.and_, filter_clauses)).prefetch_related('authors')
        for obj in queryset:
            obj_dict[obj] = obj.authors.all()

    elif filter_clauses and model_name == 'author':
        queryset = AuthorMod.objects.filter(
            reduce(operator.and_, filter_clauses)).prefetch_related('books')
        for obj in queryset:
            obj_dict[obj] = obj.books.all()
    else:
        raise ValueError('Wrong filter params or model type')



    temp = ''
    for key, value in obj_dict.items():
        for item in value:
            temp += str(item) + ', '
            result[str(key)] = temp
        temp = ''


    return result

def check_author_id(author_id):
    if not AuthorMod.objects.filter(pk=author_id).prefetch_related('books'):
        return JsonResponse({'Messages': 'No Author Found', 'Status Code': '404'
                             })
    else:
        author_obj = \
        AuthorMod.objects.filter(pk=author_id).prefetch_related('books')[0]

    return author_obj

def check_book_id(book_id):
    if not BookMod.objects.filter(pk=book_id).prefetch_related('authors'):
        return JsonResponse({'Messages': 'No Book Found', 'Status Code': '404'
                             })
    else:
        book_obj = \
        BookMod.objects.filter(pk=book_id).prefetch_related('authors')[0]

    return book_obj