from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
import random
from django.db.models import Count, Avg, Q, F
from django.db import models
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from datetime import datetime

from .serializers import (
    CategorySerializer, SubCategorySerializer, ProductSerializer,
    ProductVariantSerializer, ProductDiscountSerializer,
      FlashSaleSerializer,
    FlashSaleItemSerializer, ProductReviewSerializer
)

from .models import (
    Category, SubCategory, Product, ProductVariant,
      FlashSale, FlashSaleItem, ProductReview, ProductDiscount
)

User = get_user_model()

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        return Category.objects.prefetch_related('subcategories').annotate(product_count=Count('products')).order_by('-product_count')

    @action(detail=False, methods=['get'], url_path='homecategories')
    def homecategories(self, request):
        """Returns 5 random categories for the homepage."""
        # Use a simpler queryset for random selection
        queryset = Category.objects.all()
        shuffled_queryset = list(queryset)
        random.shuffle(shuffled_queryset)
        
        # Take first 5 items
        selected_categories = shuffled_queryset[:5]
        
        # Now get the full data with annotations for the selected categories
        full_queryset = Category.objects.prefetch_related('subcategories').annotate(
            product_count=Count('products')
        ).filter(id__in=[cat.id for cat in selected_categories])
        
        serializer = self.get_serializer(full_queryset, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related('store', 'category', 'subcategory').prefetch_related('variants', 'reviews').filter(status='published')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['brand', 'is_featured', 'status', 'store', 'category', 'subcategory']
    search_fields = ['name', 'description', 'brand']
    ordering_fields = ['name', 'base_price', 'current_price', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Enhanced filtering with price range, stock status, and advanced search.
        Only shows published products for public access.
        """
        queryset = super().get_queryset()

        # Subcategory filter
        subcategory_id = self.request.query_params.get('subcategory', None)
        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)

        # Store filter
        store_id = self.request.query_params.get('store', None)
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        # Price range filter
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(current_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(current_price__lte=max_price)

        # Stock status filter
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
        elif in_stock == 'false':
            queryset = queryset.filter(stock=0)

        # On sale filter
        on_sale = self.request.query_params.get('on_sale', None)
        if on_sale == 'true':
            queryset = queryset.filter(discounts__is_active=True)
        elif on_sale == 'false':
            queryset = queryset.filter(discounts__isnull=True)

        # Featured filter
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        elif featured == 'false':
            queryset = queryset.filter(is_featured=False)

        # Status filter
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Brand filter
        brand = self.request.query_params.get('brand', None)
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        # Advanced search
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__icontains=search_query) |
                Q(sku__icontains=search_query)
            )

        return queryset

    @action(detail=False, methods=['get'], url_path='homeproducts')
    def homeproducts(self, request):
        """Returns 5 random products for the homepage."""
        # Use a simpler queryset for random selection
        queryset = Product.objects.all()
        shuffled_queryset = list(queryset)
        random.shuffle(shuffled_queryset)
        
        # Take first 5 items
        selected_products = shuffled_queryset[:5]
        
        # Now get the full data with related fields for the selected products
        full_queryset = Product.objects.select_related('store', 'category', 'subcategory').prefetch_related(
            'variants', 'reviews'
        ).filter(id__in=[prod.id for prod in selected_products])
        
        serializer = self.get_serializer(full_queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """Returns products from the same category and store, excluding the product itself."""
        product = self.get_object()
        
        # First try: same category and same store
        queryset = self.get_queryset().filter(
            category=product.category,
            store=product.store
        ).exclude(id=product.id)[:10]
        
        # If no results, fallback to same category only
        if not queryset.exists():
            queryset = self.get_queryset().filter(
                category=product.category
            ).exclude(id=product.id)[:10]
        
        # Add debug information
        debug_info = {
            'product_id': str(product.id),
            'product_name': product.name,
            'category_id': str(product.category.id),
            'category_name': product.category.name,
            'store_id': str(product.store.id),
            'store_name': product.store.name,
            'same_store_count': self.get_queryset().filter(
                category=product.category,
                store=product.store
            ).exclude(id=product.id).count(),
            'same_category_count': self.get_queryset().filter(
                category=product.category
            ).exclude(id=product.id).count(),
            'total_products_in_category': self.get_queryset().filter(
                category=product.category
            ).count(),
            'fallback_used': not self.get_queryset().filter(
                category=product.category,
                store=product.store
            ).exclude(id=product.id).exists()
        }
        
        paginated_queryset = self.paginate_queryset(queryset)
        
        # Handle pagination more carefully for small result sets
        if queryset.count() <= 10:
            paginated_queryset = None
            debug_info['pagination_skipped'] = True
            debug_info['reason'] = 'Small result set (≤10 items)'
        
        serializer = self.get_serializer(paginated_queryset, many=True) if paginated_queryset is not None else self.get_serializer(queryset, many=True)
        
        response_data = {
            'similar_products': serializer.data,
            'debug_info': debug_info
        }
        
        return self.get_paginated_response(response_data) if paginated_queryset is not None else Response(response_data)

    @action(detail=True, methods=['get'], url_path='similar-other-stores')
    def similar_other_stores(self, request, pk=None):
        """Returns products from the same category but different stores, excluding the product itself."""
        product = self.get_object()
        
        # Get all products in the same category
        same_category_products = self.get_queryset().filter(category=product.category)
        
        # Get products from other stores
        other_stores_products = same_category_products.exclude(
            id=product.id,
            store=product.store
        )
        
        queryset = other_stores_products[:10]
        
        # Add detailed debug information
        debug_info = {
            'product_id': str(product.id),
            'product_name': product.name,
            'category_id': str(product.category.id),
            'category_name': product.category.name,
            'store_id': str(product.store.id),
            'store_name': product.store.name,
            'other_stores_count': other_stores_products.count(),
            'total_products_in_category': same_category_products.count(),
            'unique_stores_in_category': same_category_products.values('store').distinct().count(),
            'all_products_in_category': list(same_category_products.values('id', 'name', 'store__id', 'store__name')),
            'other_stores_products': list(other_stores_products.values('id', 'name', 'store__id', 'store__name')),
            'current_product_store': {
                'id': str(product.store.id),
                'name': product.store.name
            }
        }
        
        paginated_queryset = self.paginate_queryset(queryset)
        
        # Handle pagination more carefully for small result sets
        if queryset.count() <= 10:
            paginated_queryset = None
            debug_info['pagination_skipped'] = True
            debug_info['reason'] = 'Small result set (≤10 items)'
        
        serializer = self.get_serializer(paginated_queryset, many=True) if paginated_queryset is not None else self.get_serializer(queryset, many=True)
        
        response_data = {
            'similar_products_other_stores': serializer.data,
            'debug_info': debug_info
        }
        
        return self.get_paginated_response(response_data) if paginated_queryset is not None else Response(response_data)

    @action(detail=False, methods=['get'], url_path='myproducts')
    def myproducts(self, request):
        """
        Returns products for the currently authenticated user, based on
        the stores they own.
        """
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        queryset = self.get_queryset().filter(store__owner=request.user)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data) if paginated_queryset is not None else Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='featured')
    def featured(self, request):
        """Returns only featured products."""
        queryset = self.get_queryset().filter(is_featured=True)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data) if paginated_queryset is not None else Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='on-sale')
    def on_sale(self, request):
        """Returns products that are currently on sale."""
        queryset = self.get_queryset().filter(
            discounts__is_active=True
        ).distinct()
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data) if paginated_queryset is not None else Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """Returns products with low stock (less than 5 items)."""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        queryset = self.get_queryset().filter(
            store__owner=request.user,
            stock__lt=5
        )
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data) if paginated_queryset is not None else Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='popular')
    def popular(self, request):
        """Returns most reviewed products."""
        queryset = self.get_queryset().annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).filter(review_count__gt=0).order_by('-review_count', '-avg_rating')
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data) if paginated_queryset is not None else Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='productbycategory')
    def productbycategory(self, request):
        """Returns products filtered by category."""
        category_id = request.query_params.get('categoryId', None)
        subcategory_id = request.query_params.get('subcategoryId', None)
        
        if not category_id and not subcategory_id:
            return Response(
                {"error": "Either category_id or subcategory_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use a more inclusive queryset for category filtering
        queryset = Product.objects.select_related('store', 'category', 'subcategory').prefetch_related('variants', 'reviews')
        
        # Filter by category
        if category_id:
            try:
                from .models import Category
                category = Category.objects.get(id=category_id)
                queryset = queryset.filter(category=category)
            except Category.DoesNotExist:
                return Response(
                    {"error": f"Category with id {category_id} not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Filter by subcategory (additional filter)
        if subcategory_id:
            try:
                from .models import SubCategory
                subcategory = SubCategory.objects.get(id=subcategory_id)
                queryset = queryset.filter(subcategory=subcategory)
            except SubCategory.DoesNotExist:
                return Response(
                    {"error": f"Subcategory with id {subcategory_id} not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Apply additional filters from query params
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(current_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(current_price__lte=max_price)
        
        # Status filter (optional)
        status_filter = request.query_params.get('status', 'published')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Sort options
        sort_by = request.query_params.get('sort', 'newest')
        if sort_by == 'price_low':
            queryset = queryset.order_by('current_price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-current_price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'popular':
            queryset = queryset.annotate(
                review_count=Count('reviews')
            ).order_by('-review_count')
        else:  # newest (default)
            queryset = queryset.order_by('-created_at')
        
        # Debug information
        debug_info = {
            'category_id': category_id,
            'status_filter': status_filter,
            'total_before_pagination': queryset.count(),
            'queryset_sql': str(queryset.query),
            'sample_products': list(queryset[:5].values('id', 'name', 'status', 'category__name'))
        }
        
        # Handle pagination more carefully
        try:
            # If we have 10 or fewer products, skip pagination to avoid issues
            if queryset.count() <= 10:
                paginated_queryset = None
                debug_info['pagination_skipped'] = True
                debug_info['reason'] = 'Small result set (≤10 items)'
            else:
                paginated_queryset = self.paginate_queryset(queryset)
                debug_info['pagination_applied'] = paginated_queryset is not None
                debug_info['paginated_count'] = len(paginated_queryset) if paginated_queryset else 0
        except Exception as pagination_error:
            debug_info['pagination_error'] = str(pagination_error)
            paginated_queryset = None
        
        # Add error handling for serialization
        try:
            if paginated_queryset is not None:
                serializer = self.get_serializer(paginated_queryset, many=True)
                products_data = serializer.data
            else:
                # If pagination failed, serialize the full queryset
                serializer = self.get_serializer(queryset, many=True)
                products_data = serializer.data
        except Exception as e:
            # If serialization fails, try to get basic product info
            products_data = []
            target_queryset = paginated_queryset if paginated_queryset is not None else queryset
            for product in target_queryset:
                try:
                    products_data.append({
                        'id': str(product.id),
                        'name': product.name,
                        'status': product.status,
                        'error': 'Serialization failed'
                    })
                except Exception as product_error:
                    products_data.append({
                        'id': str(product.id) if hasattr(product, 'id') else 'unknown',
                        'error': f'Product error: {str(product_error)}'
                    })
            debug_info['serialization_error'] = str(e)
        
        # Add category info to response
        response_data = {
            'category_info': {
                'id': str(category.id) if category_id else None,
                'name': category.name if category_id else None,
                'subcategory_id': str(subcategory.id) if subcategory_id else None,
                'subcategory_name': subcategory.name if subcategory_id else None,
            },
            'total_products': queryset.count(),
            'products': products_data,
            'debug_info': debug_info  # Add debug info to help troubleshoot
        }
        
        return self.get_paginated_response(response_data) if paginated_queryset is not None else Response(response_data)

    @action(detail=True, methods=['get'], url_path='analytics')
    def analytics(self, request, pk=None):
        """Returns product performance metrics."""
        product = self.get_object()
        
        # Get review statistics
        reviews = product.reviews.all()
        total_reviews = reviews.count()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[f'{i}_star'] = reviews.filter(rating=i).count()
        
        analytics_data = {
            'product_id': product.id,
            'product_name': product.name,
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': rating_distribution,
            'stock_level': product.stock,
            'is_on_sale': product.on_sale,
            'current_price': str(product.current_price),
            'base_price': str(product.base_price),
            'discount_percentage': product.discount_percentage,
            'created_at': product.created_at,
            'last_updated': product.updated_at
        }
        
        return Response(analytics_data)

    @action(detail=False, methods=['get'], url_path='debug-category')
    def debug_category(self, request):
        """Debug endpoint to check category filtering."""
        category_id = self.request.query_params.get('category', None)
        if not category_id:
            return Response({"error": "No category ID provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if category exists
        try:
            from .models import Category
            category = Category.objects.get(id=category_id)
            products_in_category = Product.objects.filter(category=category).count()
            
            debug_info = {
                'category_id': category_id,
                'category_name': category.name,
                'category_exists': True,
                'total_products_in_category': products_in_category,
                'products': list(Product.objects.filter(category=category).values('id', 'name', 'status'))
            }
        except Category.DoesNotExist:
            debug_info = {
                'category_id': category_id,
                'category_exists': False,
                'error': 'Category not found'
            }
        
        return Response(debug_info)

    @action(detail=False, methods=['get'], url_path='debug-categories')
    def debug_categories(self, request):
        """Debug endpoint to show all categories with product counts."""
        from .models import Category
        from django.db.models import Count
        
        categories = Category.objects.annotate(
            product_count=Count('products')
        ).values('id', 'name', 'product_count').order_by('-product_count')
        
        debug_info = {
            'total_categories': categories.count(),
            'categories_with_products': categories.filter(product_count__gt=0).count(),
            'categories_without_products': categories.filter(product_count=0).count(),
            'all_categories': list(categories)
        }
        
        return Response(debug_info)

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulkcreate(self, request):
        """Create multiple products at once."""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        products_data = request.data.get('products', [])
        if not products_data:
            return Response({"error": "No products data provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        created_products = []
        errors = []
        
        for product_data in products_data:
            try:
                serializer = self.get_serializer(data=product_data)
                serializer.is_valid(raise_exception=True)
                product = serializer.save()
                created_products.append(product)
            except Exception as e:
                errors.append(f"Error creating product {product_data.get('name', 'Unknown')}: {str(e)}")
        
        if created_products:
            serializer = self.get_serializer(created_products, many=True)
            response_data = {
                'created_products': serializer.data,
                'total_created': len(created_products),
                'errors': errors
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'], url_path='bulk-update')
    def bulkupdate(self, request):
        """Update multiple products at once."""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        updates_data = request.data.get('updates', [])
        if not updates_data:
            return Response({"error": "No updates data provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        updated_products = []
        errors = []
        
        for update_data in updates_data:
            product_id = update_data.get('id')
            if not product_id:
                errors.append("Product ID is required for updates")
                continue
                
            try:
                product = Product.objects.get(id=product_id, store__owner=request.user)
                serializer = self.get_serializer(product, data=update_data, partial=True)
                serializer.is_valid(raise_exception=True)
                updated_product = serializer.save()
                updated_products.append(updated_product)
            except Product.DoesNotExist:
                errors.append(f"Product with ID {product_id} not found or not owned by user")
            except Exception as e:
                errors.append(f"Error updating product {product_id}: {str(e)}")
        
        if updated_products:
            serializer = self.get_serializer(updated_products, many=True)
            response_data = {
                'updated_products': serializer.data,
                'total_updated': len(updated_products),
                'errors': errors
            }
            return Response(response_data)
        else:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='productsbystore')
    def productsbystore(self, request):
        """Returns products filtered by store with optional filtering."""
        store_id = request.query_params.get('store', None)
        
        if not store_id:
            return Response(
                {"error": "Store ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use a more inclusive queryset for store filtering
        queryset = Product.objects.select_related('store', 'category', 'subcategory').prefetch_related('variants', 'reviews')
        
        # Filter by store
        try:
            from store.models import Store
            store = Store.objects.get(id=store_id)
            queryset = queryset.filter(store=store)
        except Store.DoesNotExist:
            return Response(
                {"error": f"Store with id {store_id} not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Apply additional filters from query params
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(current_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(current_price__lte=max_price)
        
        # Status filter (optional)
        status_filter = request.query_params.get('status', 'published')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Category filter
        category_id = request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Brand filter
        brand = request.query_params.get('brand', None)
        if brand:
            queryset = queryset.filter(brand__icontains=brand)
        
        # Sort options
        sort_by = request.query_params.get('sort', 'newest')
        if sort_by == 'price_low':
            queryset = queryset.order_by('current_price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-current_price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'popular':
            queryset = queryset.annotate(
                review_count=Count('reviews')
            ).order_by('-review_count')
        elif sort_by == 'featured':
            queryset = queryset.order_by('-is_featured', '-created_at')
        else:  # newest (default)
            queryset = queryset.order_by('-created_at')
        
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True) if paginated_queryset is not None else self.get_serializer(queryset, many=True)
        
        response_data = {
            'store_info': {
                'id': str(store.id),
                'name': store.name,
                'is_verified': store.is_verified,
                'location': store.location
            },
            'total_products': queryset.count(),
            'data': serializer.data
        }
        
        return self.get_paginated_response(response_data) if paginated_queryset is not None else Response(response_data)

    @action(detail=True, methods=['get'], url_path='smart-similar')
    def smart_similar(self, request, pk=None):
        """Returns smart similar products based on category, brand, and other criteria."""
        product = self.get_object()
        
        # Get all products from the same store
        store_products = self.get_queryset().filter(store=product.store).exclude(id=product.id)
        
        # Calculate similarity scores for each product
        similar_products = []
        for store_product in store_products:
            score = 0
            
            # Category match (highest weight)
            if store_product.category == product.category:
                score += 50
            
            # Brand match (high weight)
            if store_product.brand.lower() == product.brand.lower():
                score += 30
            
            # Subcategory match (medium weight)
            if store_product.subcategory and product.subcategory and store_product.subcategory == product.subcategory:
                score += 20
            
            # Price range similarity (medium weight)
            price_diff = abs(store_product.current_price - product.current_price)
            price_ratio = price_diff / product.current_price
            if price_ratio <= 0.2:  # Within 20% price range
                score += 15
            elif price_ratio <= 0.5:  # Within 50% price range
                score += 10
            
            # Featured status bonus
            if store_product.is_featured:
                score += 5
            
            # Rating bonus
            if hasattr(store_product, 'average_rating') and store_product.average_rating:
                score += min(store_product.average_rating * 2, 10)  # Max 10 points for rating
            
            # Only include products with some similarity
            if score > 0:
                similar_products.append({
                    'product': store_product,
                    'score': score,
                    'similarity_reasons': []
                })
                
                # Add similarity reasons
                if store_product.category == product.category:
                    similar_products[-1]['similarity_reasons'].append('Same category')
                if store_product.brand.lower() == product.brand.lower():
                    similar_products[-1]['similarity_reasons'].append('Same brand')
                if store_product.subcategory and product.subcategory and store_product.subcategory == product.subcategory:
                    similar_products[-1]['similarity_reasons'].append('Same subcategory')
                if store_product.is_featured:
                    similar_products[-1]['similarity_reasons'].append('Featured product')
        
        # Sort by similarity score (highest first)
        similar_products.sort(key=lambda x: x['score'], reverse=True)
        
        # Take top 10 products
        top_products = similar_products[:10]
        
        # Serialize the products
        products_data = []
        for item in top_products:
            product_data = self.get_serializer(item['product']).data
            product_data['similarity_score'] = item['score']
            product_data['similarity_reasons'] = item['similarity_reasons']
            products_data.append(product_data)
        
        # Add debug information
        debug_info = {
            'product_id': str(product.id),
            'product_name': product.name,
            'category_id': str(product.category.id),
            'category_name': product.category.name,
            'brand': product.brand,
            'store_id': str(product.store.id),
            'store_name': product.store.name,
            'total_store_products': store_products.count(),
            'similar_products_found': len(similar_products),
            'similarity_criteria': {
                'category_match_weight': 50,
                'brand_match_weight': 30,
                'subcategory_match_weight': 20,
                'price_similarity_weight': 15,
                'featured_bonus': 5,
                'rating_bonus_max': 10
            }
        }
        
        response_data = {
            'similar_products': products_data,
            'debug_info': debug_info
        }
        
        return Response(response_data)

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['variant_type', 'pricing_mode', 'is_active', 'product']
    search_fields = ['name', 'sku', 'product__name']
    ordering_fields = ['name', 'current_price', 'stock', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Enhanced filtering for variants"""
        queryset = super().get_queryset().select_related('product')
        
        # Product filter
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Variant type filter
        variant_type = self.request.query_params.get('variant_type', None)
        if variant_type:
            queryset = queryset.filter(variant_type=variant_type)
        
        # Pricing mode filter
        pricing_mode = self.request.query_params.get('pricing_mode', None)
        if pricing_mode:
            queryset = queryset.filter(pricing_mode=pricing_mode)
        
        # Stock filter
        in_stock = self.request.query_params.get('in_stock', None)
        if in_stock == 'true':
            queryset = queryset.filter(stock__gt=0)
        elif in_stock == 'false':
            queryset = queryset.filter(stock=0)
        
        # Price range filter
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price or max_price:
            # This is a simplified filter - in production you might want to calculate current_price
            if min_price:
                queryset = queryset.filter(
                    models.Q(individual_price__gte=min_price) | 
                    models.Q(price_adjustment__gte=min_price)
                )
            if max_price:
                queryset = queryset.filter(
                    models.Q(individual_price__lte=max_price) | 
                    models.Q(price_adjustment__lte=max_price)
                )
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='by-type')
    def by_type(self, request):
        """Get variants grouped by type"""
        variant_type = request.query_params.get('type', None)
        if not variant_type:
            return Response(
                {"error": "Variant type is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(variant_type=variant_type)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data) if paginated_queryset is not None else Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='size-variants')
    def size_variants(self, request):
        """Get only size variants"""
        product_id = request.query_params.get('product', None)
        if product_id:
            queryset = self.get_queryset().filter(product_id=product_id, variant_type='size')
        else:
            queryset = self.get_queryset().filter(variant_type='size')
        
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data) if paginated_queryset is not None else Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='color-variants')
    def color_variants(self, request):
        """Get only color variants"""
        product_id = request.query_params.get('product', None)
        if product_id:
            queryset = self.get_queryset().filter(product_id=product_id, variant_type='color')
        else:
            queryset = self.get_queryset().filter(variant_type='color')
        
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data) if paginated_queryset is not None else Response(serializer.data)

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def get_queryset(self):
        category_id = self.request.query_params.get('category', None)
        if category_id:
            return SubCategory.objects.filter(category_id=category_id)
        return SubCategory.objects.all()

class FlashSaleViewSet(viewsets.ModelViewSet):
    queryset = FlashSale.objects.all()
    serializer_class = FlashSaleSerializer

class FlashSaleItemViewSet(viewsets.ModelViewSet):
    queryset = FlashSaleItem.objects.all()
    serializer_class = FlashSaleItemSerializer

class ProductDiscountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product discounts"""
    serializer_class = ProductDiscountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get discounts for products owned by the authenticated user"""
        return ProductDiscount.objects.filter(
            product__store__owner=self.request.user
        ).select_related('product')
    
    def perform_create(self, serializer):
        """Create discount with validation"""
        product = serializer.validated_data['product']
        
        # Check if user owns the product
        if product.store.owner != self.request.user:
            raise PermissionDenied("You can only create discounts for your own products")
        
        serializer.save()

class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        product_pk = self.kwargs.get('product_pk')
        if product_pk:
            return ProductReview.objects.filter(product_id=product_pk)
        return ProductReview.objects.none()

    def create(self, request, *args, **kwargs):
        product_pk = self.kwargs.get('product_pk')
        product = get_object_or_404(Product, pk=product_pk)
        user = request.user

        try:
            review = ProductReview.objects.get(product=product, user=user)
            serializer = self.get_serializer(review, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except ProductReview.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        product_pk = self.kwargs.get('product_pk')
        product = get_object_or_404(Product, pk=product_pk)
        serializer.save(user=self.request.user, product=product)



