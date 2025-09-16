from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, name, phone, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone=phone,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, password=None):
        """
        Creates and saves a superuser with the given email, name, phone
        and password.
        """
        user = self.create_user(
            email,
            name=name,
            phone=phone, 
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user