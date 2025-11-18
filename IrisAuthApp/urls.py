from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path("UserLogin", views.UserLogin, name="UserLogin"),
	       path("Login.html", views.Login, name="Login"),
	       path("Register.html", views.Register, name="Register"),
	       path("RegisterAction", views.RegisterAction, name="RegisterAction"),		
	       path("PostMessage.html", views.PostMessage, name="PostMessage"),
	       path("PostMessageAction", views.PostMessageAction, name="PostMessageAction"),	
	       path("ViewMessage", views.ViewMessage, name="ViewMessage"),
]