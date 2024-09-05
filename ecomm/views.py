from django.shortcuts import render,HttpResponseRedirect,redirect
from .forms import SignUpForm,LoginForm,PostForm,EditUserProfileForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from .models import Post,Cart, CartItem
from django.contrib.auth.models import Group,User
from django.contrib.auth.forms import PasswordChangeForm,SetPasswordForm
from django.contrib.auth.decorators import login_required

# Create your views here.

# Home View

def home(request):
    name = request.user.username
    posts = Post.objects.all()
    return render(request,'ecomm/home.html',{'name': name, 'posts': posts})

# SignUp View
def user_signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            messages.success(request,'Account Created Successfully..!!')
            user = form.save()
            group = Group.objects.get(name='User')
            user.groups.add(group)
    else:
        form = SignUpForm()
    return render(request,'ecomm/signup.html',{'form':form})

# Login View
def user_login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = LoginForm(request=request,data=request.POST)
            if form.is_valid():
                uname = form.cleaned_data['username']
                upass = form.cleaned_data['password']
                user = authenticate(username=uname,password=upass)
                if user is not None:
                    login(request,user)
                    messages.success(request,'Logged in successfully..!!')
                    return HttpResponseRedirect('/home/')
        else:
            form = LoginForm()
        return render(request,'ecomm/login.html',{'form':form})
    else:
        return HttpResponseRedirect('/dashboard/')

# About View
def about(request):
    return render(request,'ecomm/about.html')

# Contact View
def contact(request):
    return render(request,'ecomm/contact.html')

# Dashboard View
def dashboard(request):
    if request.user.is_authenticated:
        posts = Post.objects.all()
        return render(request,'ecomm/dashboard.html',{'posts':posts})
    else:
        return HttpResponseRedirect('/login/')

# Display All Users View
def display_users(request):
    if request.user.is_authenticated:
        current_user = request.user
        users = User.objects.exclude(pk=current_user.pk)
        return render(request,'ecomm/users.html',{'users': users})
    else:
        return HttpResponseRedirect('/login/')

def user_details(request, user_id):
    if request.user.is_authenticated:
        name = request.user.username
        user = User.objects.get(id=user_id)
        return render(request,'ecomm/user_details.html',{'name': name,'user': user})
    else:
        return HttpResponseRedirect('/login/')

# Profile View
def user_profile(request):
    if request.user.is_authenticated:
        name = request.user.username
        if request.method == "POST":
            fm = EditUserProfileForm(request.POST,instance=request.user)
            if fm.is_valid():
                messages.success(request,'Profile Updated successfully..!!')
                fm.save()
        else:
            fm = EditUserProfileForm(instance = request.user)
        return render(request,'ecomm/profile.html',{'name': name,'form':fm})
    else:
        return HttpResponseRedirect('/login/')

# Change Password View with old password
def user_change_pass(request):
    if request.user.is_authenticated:
        name = request.user.username
        if request.method == "POST":
            fm = PasswordChangeForm(user=request.user,data=request.POST)
            if fm.is_valid():
                fm.save()
                update_session_auth_hash(request,fm.user)
                messages.success(request,'Password changed in successfully..!!')
                return HttpResponseRedirect('/profile/')  
        else:
            fm = PasswordChangeForm(user=request.user)
        return render(request,'ecomm/changepass.html',{'name': name,'form':fm})
    else:
        return HttpResponseRedirect('/login/')
    
# Change Password View without old password
def user_change_pass1(request):
    if request.user.is_authenticated:
        name = request.user.username
        if request.method == "POST":
            fm = SetPasswordForm(user=request.user,data=request.POST)
            if fm.is_valid():
                fm.save()
                update_session_auth_hash(request,fm.user)
                messages.success(request,'Password changed in successfully..!!')
                return HttpResponseRedirect('/profile/')  
        else:
            fm = SetPasswordForm(user=request.user)
        return render(request,'ecomm/changepass1.html',{'name': name,'form':fm})
    else:
        return HttpResponseRedirect('/login/')

# Logout View
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

# Add New Post
def add_post(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product added successfully.')
                form = PostForm()
        else:
            form = PostForm()
        return render(request, 'ecomm/addpost.html', {'form': form})
    else:
        return HttpResponseRedirect('/login/')
    
# Update New Post
def update_post(request,id):
    if request.user.is_authenticated:
        if request.method == "POST":
            pi = Post.objects.get(pk=id)
            form = PostForm(request.POST,instance=pi)
            if form.is_valid():
                messages.success(request,'Products are Updated successfully..!!')
                form.save() 
        else:
            pi = Post.objects.get(pk=id)
            form = PostForm(instance=pi)
        return render(request,'ecomm/updatepost.html',{'form':form})
    else:
        return HttpResponseRedirect('/login/')
    
# Delete New Post
def delete_post(request,id):
    if request.user.is_authenticated:
        if request.method == "POST":
            pi = Post.objects.get(pk=id)
            messages.success(request,'Products are Deleted successfully..!!')
            pi.delete()
            return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponseRedirect('/login/')


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if quantity is not provided

        # Get the product
        product = Post.objects.get(pk=product_id)

        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Add the item to the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()

        return redirect('/view_cart/')  # Redirect to the cart page
    else:
        return redirect('/home/')  # Redirect to home if request method is not POST

@login_required
def view_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_items = cart.items.all()
    else:
        cart_items = []
    return render(request, 'ecomm/view_cart.html', {'cart_items': cart_items})

@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = CartItem.objects.get(pk=cart_item_id)
    cart_item.delete()
    return redirect('/view_cart/')