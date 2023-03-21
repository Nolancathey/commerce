from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    pass

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    categoryName= models.CharField(max_length=50)
    
    def __str__(self):
        return self.categoryName


class Listing(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    imageUrl = models.CharField(max_length=1000)
    price = models.FloatField()
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_owner")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")

    def __str__(self):
        return self.title

class Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    wishlist_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="wishlist_user")
    listItem = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="wishlist_item")

    
class Bid(models.Model):
    amount = models.FloatField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="bidding_user")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="bidding_item")



class Comment(models.Model):
    comment = models.CharField(max_length=300)
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="comment_user")
    commentItem = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="comment_item")


