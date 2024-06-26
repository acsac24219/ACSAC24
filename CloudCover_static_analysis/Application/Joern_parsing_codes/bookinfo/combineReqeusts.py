

from pprint import pprint
from urllib.parse import urlparse





def combineReqeusts():

    productpage=[

        {'entry': '/productpage', 'send_request': 'http://{0}{1}:9080/details/*', 'dependence': []},
        {'entry': '/productpage', 'send_request': 'http://{0}{1}:9080/reviews/*', 'dependence': []},
        {'entry': '/api/v1/products/<product_id>', 'send_request': 'http://{0}{1}:9080/details/*', 'dependence': []},
        {'entry': '/api/v1/products/<product_id>/reviews', 'send_request': 'http://{0}{1}:9080/reviews/*', 'dependence': []},
        {'entry': '/api/v1/products/<product_id>/ratings', 'send_request': 'http://{0}{1}:9080/ratings/*', 'dependence': []},
    ]


    reviews=[
        {'entry': '/reviews/{product_id}', 'send_request': 'http://ratings.bookinfo.com:9080/ratings/*', 'dependence': []}
    ]

    ratings=[
        {'condition': ['Number.isNaN(productId)',
                       'process.env.SERVICE_VERSION === v2',
                       'process.env.DB_TYPE === mysql'],
         'dependence': [],
         'entry': '/ratings/[0-9]*/',
         'send_request': 'mysql'},
        {'condition': ['Number.isNaN(productId)',
                       'process.env.SERVICE_VERSION === v2',
                       'process.env.DB_TYPE === mysql'],
         'dependence': [],
         'entry': '/ratings/[0-9]*/',
         'send_request': 'mongo'}
     ]


    details=[
        {'condition': ['ENV[ENABLE_EXTERNAL_BOOK_SERVICE] === true'],
        'dependence': [],
        'entry': '/details',
        'send_request': 'https://www.googleapis.com/books/v1/volumes?q=isbn:0486424618'}
    ]

    datasets=[
        {'entry': 'mysql',
        'send_request': ''},
        {'entry': 'mongo',
        'send_request': ''},
     ]


    combine_reqeusts_list=[]
    

    for item in productpage:
        send_request_path=urlparse(item['send_request'])[2]
        send_request_path=send_request_path[:-2]

        for other in reviews:
            entry=other['entry']
            if entry.startswith(send_request_path):
                combine_reqeusts_list.append((item,other))


        for other in ratings:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))

        for other in details:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))

        for other in datasets:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))
    

    for item in reviews:
        send_request_path=urlparse(item['send_request'])[2]
        send_request_path=send_request_path[:-2]

        for other in productpage:
            entry=other['entry']
            if entry.startswith(send_request_path):
                combine_reqeusts_list.append((item,other))


        for other in ratings:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))

        for other in details:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))

        for other in datasets:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))


    for item in ratings:
        send_request_path=urlparse(item['send_request'])[2]

        for other in productpage:
            entry=other['entry']
            if entry.startswith(send_request_path):
                combine_reqeusts_list.append((item,other))


        for other in reviews:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))

        for other in details:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))

        for other in datasets:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))


    for item in details:
        send_request_path=urlparse(item['send_request'])[2]

        for other in productpage:
            entry=other['entry']
            if entry.startswith(send_request_path):
                combine_reqeusts_list.append((item,other))


        for other in reviews:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))

        for other in ratings:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))

        for other in datasets:
            entry=other['entry']
            if send_request_path in entry:
                combine_reqeusts_list.append((item,other))


    two_requests_set=set()
    for item in combine_reqeusts_list:
        two_requests_set.add((item[0]['entry'],item[1]['entry']))



    three_requests_set=set()
    num=len(combine_reqeusts_list)
    i=0
    for i in range(num):
        for j in range(num):
            if i==j:
                continue

            start=combine_reqeusts_list[i]
            end=combine_reqeusts_list[j]

            if start[1]['entry']==end[0]['entry']:
                three_requests_set.add((start[0]['entry'],start[1]['entry'],end[1]['entry']))


    four_requests_set=set()
    num_3=len(three_requests_set)
    num_2=len(combine_reqeusts_list)
    three_requests_list=list(three_requests_set)
    i=0
    for i in range(num_3):
        for j in range(num_2):
            if i==j:
                continue

            start=three_requests_list[i]
            end=combine_reqeusts_list[j]

            if start[2]==end[0]['entry']:
                four_requests_set.add((start[0],start[1],start[2],end[1]['entry']))



    two_requests_list=list(two_requests_set)
    two_requests_list.sort()
    for item in two_requests_list:
        print(item[0]," --> ",item[1])

    print()

    three_requests_list=list(three_requests_set)
    three_requests_list.sort()
    for item in three_requests_list:
        print(item[0]," --> ",item[1]," --> ",item[2])

    print()

    four_requests_list=list(four_requests_set)
    four_requests_list.sort()
    for item in four_requests_list:
        print(item[0]," --> ",item[1]," --> ",item[2]," --> ",item[3])

if __name__ == '__main__':
    combineReqeusts()