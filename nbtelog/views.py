from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.text import Truncator
from .models import News, NewsCategory, Institution, Document, SliderImage, ChatBot
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
from django.templatetags.static import static

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    slider_queryset = SliderImage.objects.filter(is_active=True).order_by('order')

    if slider_queryset.exists():
        slider_images = [
            {
                'url': slide.image.url,
                'title': slide.title,
                'caption': slide.caption,
            }
            for slide in slider_queryset
        ]
    else:
        slider_images = [
            {
                'url': static(f'images/slide{i}.jpg'),
                'title': f'Default Slide {i}',
                'caption': '',
            }
            for i in range(1, 8)
        ]

    latest_news = News.objects.filter(status='published').order_by('-created_at')[:3]
    
    # Get featured institutions
    featured_institutions = Institution.objects.all()[:3]
    
    context = {
        'title': 'Home',
        'slider_images': slider_images,
        'latest_news': latest_news,
        'featured_institutions': featured_institutions,
    }
    return render(request, 'nbtelog/index.html', context)

def news_list(request):
    news_list = News.objects.filter(status='published').order_by('-created_at')
    categories = NewsCategory.objects.all()
    
    # Filter by category if specified
    category_slug = request.GET.get('category')
    if category_slug:
        news_list = news_list.filter(category__slug=category_slug)
    
    # Pagination
    paginator = Paginator(news_list, 5)  # 5 articles per page
    page = request.GET.get('page')
    news = paginator.get_page(page)
    
    context = {
        'title': 'News & Updates',
        'news': news,
        'categories': categories,
    }
    return render(request, 'nbtelog/news/list.html', context)

def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, status='published')
    
    # Get related news from the same category
    related_news = News.objects.filter(
        category=news.category,
        status='published'
    ).exclude(id=news.id)[:3]
    
    context = {
        'title': news.title,
        'news': news,
        'related_news': related_news,
    }
    return render(request, 'nbtelog/news/detail.html', context)

def search(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Search in News
        news_results = News.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            status='published'
        )
        
        # Search in Institutions
        institution_results = Institution.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(address__icontains=query)
        )
        
        # Process results to have consistent attributes
        processed_results = []
        
        # Process News results
        for news in news_results:
            excerpt = Truncator(news.content).words(30)
            processed_results.append({
                'title': news.title,
                'excerpt': excerpt,
                'url': news.get_absolute_url() if hasattr(news, 'get_absolute_url') else '#',
                'created_at': news.created_at,
                'type': 'News'
            })
        
        # Process Institution results
        for inst in institution_results:
            # Create an excerpt from address and other details
            details = f"Code: {inst.code} | Address: {inst.address} | Status: {inst.accreditation_status}"
            excerpt = Truncator(details).words(30)
            processed_results.append({
                'title': inst.name,
                'excerpt': excerpt,
                'url': inst.website if inst.website else '#',
                'created_at': inst.established_date,
                'type': 'Institution'
            })
        
        results = processed_results
    
    context = {
        'query': query,
        'results': results,
        'title': 'Search Results',
    }
    return render(request, 'nbtelog/search.html', context)

def about_us(request):
    context = {
        'title': 'About the National Board for Technical Education',
    }
    return render(request, 'nbtelog/about.html', context)

def servicom(request):
    context = {
        'title': 'SERVICOM - NBTE',
    }
    return render(request, 'nbtelog/servicom.html', context)

def aprs_ict(request):
    context = {
        'title': 'Academic Planning, Research, Statistics and ICT - NBTE',
    }
    return render(request, 'nbtelog/departments/aprs_ict.html', context)

def nbtecoex(request):
    context = {
        'title': 'NBTE Centre of Excellence',
    }
    return render(request, 'nbtelog/nbtecoex.html', context)

def tvet_institutions(request):
    return render(request, 'nbtelog/tvet_institutions.html', {
        'title': 'TVET Institutions'
    })

def odfel(request):
    return render(request, 'nbtelog/odfel.html', {
        'title': 'Open Distance and Flexible e-Learning (ODFeL)'
    })

def odfel_guidelines(request):
    return render(request, 'nbtelog/odfel_guidelines.html', {
        'title': 'Guidelines for ODFeL Programme'
    })

def nsq_benefits(request):
    return render(request, 'nbtelog/nsq_benefits.html', {
        'title': 'Benefits of NSQ'
    })

def nsq(request):
    return render(request, 'nbtelog/nsq.html', {
        'title': 'National Skills Qualifications (NSQ)'
    })

def nsqf(request):
    return render(request, 'nbtelog/nsqf.html', {
        'title': 'Nigerian Skills Qualifications Framework (NSQF)'
    })

def nsqf_levels(request):
    return render(request, 'nbtelog/nsqf_levels.html', {
        'title': 'NSQF 9-Level Framework'
    })

def research_development(request):
    context = {
        'title': 'Research & Development',
        'debug': settings.DEBUG
    }
    return render(request, 'nbtelog/research_development.html', context)

def downloads(request):
    try:
        # Fetch all documents and order by most recent
        documents = Document.objects.all().order_by('-uploaded_at')
        
        # Add file size information
        for doc in documents:
            try:
                doc.file.size  # This will raise an error if file is missing
            except:
                doc.file = None  # Set to None if file is missing
        
        context = {
            'title': 'Downloads',
            'documents': documents,
        }
        return render(request, 'nbtelog/downloads.html', context)
    except Exception as e:
        # Log the error for debugging
        print(f"Error in downloads view: {str(e)}")
        context = {
            'title': 'Downloads',
            'documents': [],
            'error': 'An error occurred while loading the documents.'
        }
        return render(request, 'nbtelog/downloads.html', context)

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').lower()
            
            logger.info(f"Received message: {user_message}")
            
            # Get all active chatbot entries
            chatbot_entries = ChatBot.objects.filter(is_active=True)
            logger.info(f"Found {chatbot_entries.count()} active chatbot entries")
            
            if not chatbot_entries:
                logger.warning("No active chatbot entries found")
                return JsonResponse({
                    'response': "I'm sorry, I'm not configured yet. Please try again later."
                })
            
            # Convert QuerySet to list for easier indexing
            chatbot_entries_list = list(chatbot_entries)
            
            # Prepare data for similarity matching
            questions = [entry.question.lower() for entry in chatbot_entries_list]
            keywords_list = [entry.keywords.lower().split(',') for entry in chatbot_entries_list]
            
            logger.info(f"Processing {len(questions)} questions for matching")
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(questions + [user_message])
            
            # Calculate similarity scores
            similarity_scores = cosine_similarity(
                tfidf_matrix[-1:], 
                tfidf_matrix[:-1]
            )[0]
            
            # Get the best match
            best_match_idx = int(np.argmax(similarity_scores))  # Convert to Python int
            best_match_score = float(similarity_scores[best_match_idx])  # Convert to Python float
            
            logger.info(f"Best match score: {best_match_score}")
            
            # Check if the match is good enough
            if best_match_score > 0.3:  # Threshold for matching
                response = chatbot_entries_list[best_match_idx].answer
                logger.info(f"Using similarity match: {response[:50]}...")
            else:
                # Check for keyword matches
                keyword_matches = []
                for idx, keywords in enumerate(keywords_list):
                    matches = [k for k in keywords if k in user_message]
                    if matches:
                        keyword_matches.append((idx, len(matches)))
                        logger.info(f"Found keyword matches: {matches}")
                
                if keyword_matches:
                    # Get the entry with most keyword matches
                    best_keyword_match = max(keyword_matches, key=lambda x: x[1])
                    response = chatbot_entries_list[best_keyword_match[0]].answer
                    logger.info(f"Using keyword match: {response[:50]}...")
                else:
                    response = "I'm sorry, I don't understand your question. Please try rephrasing or contact our support team."
                    logger.info("No matches found, using default response")
            
            return JsonResponse({
                'response': response,
                'confidence': best_match_score if best_match_score > 0.3 else 0.0
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({
                'response': "I'm sorry, I couldn't understand your message format.",
                'error': str(e)
            })
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JsonResponse({
                'response': "I'm sorry, I encountered an error. Please try again later.",
                'error': str(e)
            })
    
    return JsonResponse({'error': 'Invalid request method'})
