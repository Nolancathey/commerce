from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.core.validators import MaxValueValidator
from builtins import max


from .models import User
from .models import Listing, Category, Wishlist, Bid, Comment


def index(request):
    listing = Listing.objects.filter(isActive=True)
    if 'unlist' in request.POST and request.POST['unlist'] != None:
        try:
            title = request.POST['unlist']
            item = Listing.objects.get(title=title)
            highest_bid = Bid.objects.filter(item=item).order_by('-amount').first()
            item.isActive = False
            item.save()
            if highest_bid:
                bid = highest_bid.bidder
                message = f"The auction for {item.title} has ended. {bid} won the auction with a bid of {highest_bid.amount}."
            else:
                message = f"The auction for {item.title} has ended. No one won the auction."
        except Listing.DoesNotExist:
            message = f"The item {title} does not exist."
    else:
        message = ""
    return render(request, "auctions/index.html", {'message': message, 'listing': listing})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def listing(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST.get('description')
        imageUrl = request.POST.get('imageUrl')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        category = Category.objects.get(categoryName=category_id)
        user = request.user
        owner = user
        
        
        listing = Listing(title=title, description=description, imageUrl=imageUrl, price=price, category=category, owner=owner)
        listing.save()
        return redirect('index') 
    else:
        return render(request, "auctions/listing.html")


def item(request, title):
    if request.method == "POST":
        data = Listing.objects.get(title=title)
        if 'comment' in request.POST and request.POST['comment'] is not None:
            user = request.user
            post = request.POST['comment']
            com = Comment(comment=post, comment_user=user, commentItem=data)
            com.save()
        else:
            if Comment.objects.all() is not None:
                comment = Comment.objects.all()
                return render(request, "auctions/item.html", {'data': data, 'comment': comment})
            else:
                return render(request, "auctions/item.html", {'data': data})
    else:
        if Comment.objects.all() is not None:
                comment = Comment.objects.all()
                data = Listing.objects.get(title=title)
                return render(request, "auctions/item.html", {'data': data, 'comment': comment})
        else:
            data = Listing.objects.get(title=title)
            return render(request, "auctions/item.html", {'data': data})

def category(request):
    if request.method == "POST":
        categoryform = request.POST['category']
        category = Category.objects.get(categoryName=categoryform)
        data = Listing.objects.filter(category=category, isActive=True)
        return render(request, "auctions/category.html", {'data': data})

    else:
        return render(request, "auctions/category.html")

@login_required
def wishlist(request):
    if request.method == "POST":
        user = request.user
        if 'title'  in request.POST:
            title = request.POST['title']
            try:
                title = request.POST['title']
                listing = Listing.objects.get(title=title)
                wishlist_item, created = Wishlist.objects.get_or_create(wishlist_user=user, listItem=listing)
                if not created:
                    messages.info(request, "Item already in wishlist.")
                else:
                    wishlist_item.save()
            except listing.DoesNotExist:
                pass
        elif 'delete' in request.POST:
            title = request.POST['delete']
            try:
                listing = Listing.objects.get(title=title)
                wishlist_item = Wishlist.objects.filter(wishlist_user=user, listItem=listing)
                wishlist_item.delete()
            except (Listing.DoesNotExist, Wishlist.DoesNotExist):
                pass
        wishlist_items = Wishlist.objects.filter(wishlist_user=request.user)
        return render(request, "auctions/wishlist.html", {'wishlist': wishlist_items})
    else:
        wishlist_items = Wishlist.objects.filter(wishlist_user=request.user)
        return render(request, "auctions/wishlist.html", {'wishlist': wishlist_items})

@login_required
def bid(request, title):
    item = Listing.objects.get(title=title)
    highest_bid = Bid.objects.filter(item=item).order_by('-amount').first()
    if request.method == "POST":
        form = request.POST.get("bid")
        if form:
            new_bid = float(form)
            if highest_bid:
                current_highest_bid = float(highest_bid.amount)
                if new_bid > current_highest_bid:
                    highest_bid.amount = new_bid
                    highest_bid.bidder = request.user
                    highest_bid.save()
                    return redirect("auctions:item", title=title)
                else:
                    messages.error(request, "Your bid must be higher than the current highest bid.")
                    return render(request, 'auctions/bid.html', {'item': item, 'highest_bid': highest_bid})
            else:
                highest_bid = float(item.price)
                if new_bid > current_highest_bid:
                    bid = Bid(amount=new_bid, bidder=request.user, item=item)
                    bid.save()
                    return redirect("auctions:item", title=title)
                else:
                    messages.error(request, "Your bid must be higher than the price.")
                    return render(request, 'auctions/bid.html', {'item': item, 'highest_bid': highest_bid})
        else:
            messages.error(request, "Please enter a valid bid amount.")
            return render(request, 'auctions/bid.html', {'item': item, 'highest_bid': highest_bid})
    else:
        return render(request, 'auctions/bid.html', {'item': item, 'highest_bid': highest_bid})