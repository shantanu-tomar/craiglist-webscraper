import requests
import datetime, timeago
from requests.compat import quote_plus
from django.shortcuts import render
from bs4 import BeautifulSoup
from .models import Search, VisitedPost
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator,  EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.http import HttpResponse
import smtplib
from email.message import EmailMessage
#from dotenv import load_dotenv
import os



#BASE_CRAIGSLIST_URL = "https://delhi.craigslist.org/search/sss?query={}&sort={}&min_price={}&max_price={}&s={}"
BASE_CRAIGSLIST_URL = "https://losangeles.craigslist.org/search/sss?query={}&sort={}&min_price={}&max_price={}&s={}"
BASE_IMG_URL = "https://images.craigslist.org/{}_300x300.jpg"


def home(request):
    return render(request, 'home.html')
    
@csrf_exempt    
def new_search(request):

    if request.method == 'POST':
        #last_query = request.session['last_query']
        query = request.POST.get('search')
        request.session['last_query'] = query
        page_no = 1
    
        Search.objects.create(search = query)       #creates a database of all queries & sort
        min_price = request.POST.get('price_min','')
        max_price = request.POST.get('price_max','')
        sort_param = request.POST.get('sort_param', 'rel')
        
        first_page_url = BASE_CRAIGSLIST_URL.format(quote_plus(query), sort_param, min_price, max_price, '0')
        #print(final_url)
        response = requests.get(first_page_url)
        data = response.text
        soup = BeautifulSoup(data, 'html.parser')
        
        total_items = int(soup.find(class_ = 'totalcount').text)
        request.session['total_items'] = total_items
        
        pages = total_items // 120
        remainder = total_items % 120

        if remainder != 0:
            pages += 1 
        
        final_postings = []
        for page in range(pages):
            page_url = BASE_CRAIGSLIST_URL.format(quote_plus(query), sort_param, min_price, max_price, page)
            #print(final_url)
            response = requests.get(page_url)
            data = response.text
            soup = BeautifulSoup(data, 'html.parser')
        
            post_listings = soup.find_all('li', {'class': 'result-row'})


            for post in post_listings:
                post_id = post_listings.index(post)
                post_title = post.find(class_ = 'result-title hdrlnk').text
                post_url = post.find('a').get('href')
                
                if post.find(class_ = 'result-hood'):
                    post_location = post.find(class_ = 'result-hood').text
                else:
                    continue
                    
                if post.find(class_ = 'result-image gallery'):
                    img_ids = post.find(class_ = 'result-image gallery').get('data-ids')
                    img_ids = img_ids.split(',')
                    main_img_id = img_ids[0][2:]
                    img_url = BASE_IMG_URL.format(main_img_id)
                     
                else:
                    img_url = "https://craigslist.org/images/peace.jpg"
                
                if post.find(class_ = 'result-price'):
                    post_price = post.find(class_ = 'result-price').text
                else:
                    post_price = 'N/A'
                    
                final_postings.append([post_title, post_url, post_price, post_location, img_url, post_id], )
        
            
        request.session['final_data'] = final_postings 
        paginator = Paginator(final_postings, 20)
        
        final_data = paginator.page(1)
        
        
    
    if request.method == 'GET':
        page_no = request.GET.get('page', 1)
        if page_no != 1:
            query = request.session['last_query']
    
        final_data_stored = request.session['final_data']
        total_items = request.session['total_items']
        paginator = Paginator(final_data_stored, 20)  # 20 posts per page

        #total_pages = p.num_pages
        #for page in p.page_range: #returns 1 \n ....      p.page_range returns (1,61)
            #print(page)
        #p1 = p.page(1)
        #print(p1)    #returns <Page 1 of total_pages>
        
        #print(p1.number)  #returns number of that page i.e 1
        #print(p1.object_list) #returns all posts at page 1 as a list
        
        # print(p1.has_previous() ) #returns False
        # print(p1.has_next() ) #returns True
        # print(p1.next_page_number()) #returns 2
        # #print(p1.previous_page_number()) #returns EmptyPage ERROR (page no. less than 1) !!
        
        try:
            final_data = paginator.page(page_no)
        except PageNotAnInteger:
            final_data = paginator.page(1)
        except EmptyPage:
            final_data = paginator.page(paginator.num_pages)
        
    
    stuff_for_frontend = {
        'query': query,
        'final_data': final_data,
        'total_items': total_items,
        }
    
    
    
    return render(request, 'testapp/new_search.html', stuff_for_frontend)
    #render takes 3 args: request, template, context


@csrf_exempt
def post_detail(request):
    details_url = request.POST.get('search')
    response_details = requests.get(details_url).text
    index_start = response_details.find('imgList')   #searching for the list containing links to all post imgs
    
    #extracting post id from the url
    last_slash = details_url[-1:0:-1].find('/')
    post_id = details_url[-last_slash:-5]

    database_entry = VisitedPost(post_url = details_url, post_id = post_id)
    database_entry.save()


    #if post has images-
    if index_start and (index_start != -1):
        index_start += response_details[index_start:].find('[') + 1
        index_stop = response_details[index_start:].find(']')
        imglist = response_details[index_start:index_start+index_stop]
        list_ = imglist.split('},{')
        
         
        imglist = []
        for x in list_:
            x_list = x.split(',')
            x_list = (':'.join(x_list)).split(':')

            for i in range(len(x_list)):
                if x_list[i] == '"https':
                    url = ':'.join(x_list[i:i+2])
                    imglist.append(url.strip('"'))

        imgurls = []
        for url in imglist:
            if url[-11:] == '600x450.jpg':
                imgurls.append(url)
            
        imgs = list(enumerate(imgurls, 1))
        len_imgurls = len(imgurls)
        
    elif not index_start or (index_start== -1):
        imgs = [(1,"https://craigslist.org/images/peace.jpg"),]
        len_imgurls = 1
        
            
    soup_details = BeautifulSoup(response_details, 'html.parser')
    
    post_title = soup_details.find(class_= 'postingtitletext').text
    
    post_body = soup_details.find(id = 'postingbody')
    post_body = (str(post_body)).split('<br/>')
    post_body = post_body[2:-2]
    post_notice = soup_details.find(class_= 'notices').text
    
    post_datetime = soup_details.find(class_= 'date timeago').get('datetime')[:-5].split('T')
    post_datetime = ' '.join(post_datetime)
    now = datetime.datetime.now()
    post_datetime= timeago.format(post_datetime, now)
    
    email_share = soup_details.find(class_='email-friend').get('href')
    
    stuff_for_frontend = {
            'body': post_body,
            'title': post_title,
            'price_display':'none',
            'notice': post_notice,
            'imglen': len_imgurls,
            'imgs': imgs,
            'datetime': post_datetime,
            'email_share': email_share,
            'map_display': 'none',
            'post_url': details_url,
            
        }
        
    if soup_details.find(id ='map'):
        map_lat = soup_details.find(id ='map').get('data-latitude')
        map_long = soup_details.find(id ='map').get('data-longitude')
        map_cord = map_lat +', ' +map_long
        stuff_for_frontend['map_cord']= map_cord
        stuff_for_frontend['map_display'] = ''
    

    if soup_details.find(class_='price'):
        price = soup_details.find(class_='price').text
        post_title = post_title.replace(price,'')
        stuff_for_frontend['title'] = post_title
        stuff_for_frontend['price'] = price
        stuff_for_frontend['price_display'] = ''
        
    if soup_details.find(class_='attrgroup'):
        attrgroup = soup_details.find_all(class_='attrgroup')
        attrb_text = ''
        for attrb_class in attrgroup:
            attrb_text += '\n' +attrb_class.text
        list2 = attrb_text.split('\n')
        attrb_list = []
        for i in list2 :
            if i!= '':
                attrb_list.append(i)
         
        stuff_for_frontend['attrb_list'] = attrb_list
    
    return render(request, 'testapp/post_detail.html', stuff_for_frontend)



@csrf_exempt
def share_by_mail(request):
    sender_name = request.POST['sen_name']
    recp_email = request.POST.get('rcp_mail')
    post_url = request.POST['post_url']
    
    web_email_add = os.getenv('EMAIL')
    web_email_pass = os.getenv('E_PASS')

    msg = EmailMessage()
    msg['Subject'] = subject = sender_name +' invites you !'
    msg['From'] = web_email_add
    msg['To'] = recp_email
    msg.set_content(f"Hi there!\n\n{sender_name} just invited you to visit this awesome listing at CraigsList.\n\n{post_url}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        
        smtp.login(web_email_add, web_email_pass)
        smtp.send_message(msg)

    
    return HttpResponse('')
    
