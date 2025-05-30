from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet, TransactionViewSet, PostViewSet, StoreViewSet, CategoryViewSet,
    CouponViewSet, ProductViewSet, CommentViewSet, OrderViewSet, OrderItemViewSet,
    ReportViewSet, UserVerificationViewSet, TwoFactorAuthViewSet, RoleViewSet,
    UserRoleViewSet, MagicLinkViewSet, LoginHistoryViewSet, WishlistViewSet,
    ShippingAddressViewSet, PaymentViewSet, StoreStaffViewSet, CustomerLifetimeValueViewSet,
    StoreAnalyticsViewSet, LikeViewSet, FollowViewSet, NotificationViewSet,
    SystemSettingsViewSet, CurrencyViewSet, SubscriptionPlanViewSet, AnalyticsViewSet,
    RefundViewSet, FraudDetectionViewSet, LoyaltyProgramViewSet, AuctionViewSet,
    SearchIndexViewSet, RealTimeNotificationViewSet, RateLimitViewSet, LanguageViewSet,
    SocialShareViewSet, SecurityLogViewSet, ExternalServiceViewSet,
    GDPRComplianceViewSet, InventoryViewSet, ProductVariantViewSet, DynamicPricingViewSet,
    LoyaltyPointsViewSet, SearchFilterViewSet, AbandonedCartViewSet, UserBehaviorViewSet,
    SalesReportViewSet, GroupViewSet, MessageViewSet, RepostViewSet, HashtagViewSet,
    MentionViewSet, PopularProductList, SearchProductByTitle
)

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'posts', PostViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'products', ProductViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'user-verifications', UserVerificationViewSet)
router.register(r'two-factor-auths', TwoFactorAuthViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'user-roles', UserRoleViewSet)
router.register(r'magic-links', MagicLinkViewSet)
router.register(r'login-histories', LoginHistoryViewSet)
router.register(r'wishlists', WishlistViewSet)
router.register(r'shipping-addresses', ShippingAddressViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'store-staffs', StoreStaffViewSet)
router.register(r'customer-lifetime-values', CustomerLifetimeValueViewSet)
router.register(r'store-analytics', StoreAnalyticsViewSet)
router.register(r'likes', LikeViewSet)
router.register(r'follows', FollowViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'system-settings', SystemSettingsViewSet)
router.register(r'currencies', CurrencyViewSet)
router.register(r'subscription-plans', SubscriptionPlanViewSet)
router.register(r'analytics', AnalyticsViewSet)
router.register(r'refunds', RefundViewSet)
router.register(r'fraud-detections', FraudDetectionViewSet)
router.register(r'loyalty-programs', LoyaltyProgramViewSet)
router.register(r'auctions', AuctionViewSet)
router.register(r'search-indices', SearchIndexViewSet)
router.register(r'real-time-notifications', RealTimeNotificationViewSet)
router.register(r'rate-limits', RateLimitViewSet)
router.register(r'languages', LanguageViewSet)
router.register(r'social-shares', SocialShareViewSet)
router.register(r'security-logs', SecurityLogViewSet)
router.register(r'external-services', ExternalServiceViewSet)
router.register(r'gdpr-compliances', GDPRComplianceViewSet)
router.register(r'inventories', InventoryViewSet)
router.register(r'product-variants', ProductVariantViewSet)
router.register(r'dynamic-pricings', DynamicPricingViewSet)
router.register(r'loyalty-points', LoyaltyPointsViewSet)
router.register(r'search-filters', SearchFilterViewSet)
router.register(r'abandoned-carts', AbandonedCartViewSet)
router.register(r'user-behaviors', UserBehaviorViewSet)
router.register(r'sales-reports', SalesReportViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'reposts', RepostViewSet)
router.register(r'hashtags', HashtagViewSet)
router.register(r'mentions', MentionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('popular-products/', PopularProductList.as_view(), name='popular-product-list'),
     path('/categories', CategoryViewSet.as_view(), name='categories'),
    path('search-products/', SearchProductByTitle.as_view(), name='search-product-by-title'),
]
