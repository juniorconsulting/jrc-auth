# jrc-auth

Microservice managing everything related to user authentication for JrC.
Implemented as a RESTful API served over HTTP(S).

## Setup

The API is implemented using [django-restframework](http://www.django-rest-framework.org/) with [Redis](http://redis.io/) as a key/value-store.

### Local setup

* `git clone git@github.com:juniorconsulting/jrc-auth.git`
* `cd jrc-auth && virtualenv env && pip install -r requirements.txt`
* `python manage.py migrate`
* `python manage.py runserver`

### Production environment

`jrc-auth` is running on the `jrc-services` droplet.
It is controlled using [`supervisor`](http://supervisord.org/) and is running under the `jrcauth` user.

For now, deployment is not automated, so the procedure is as follows:

* SSH to `jrc-services`.
* `sudo su - jrcauth`
* Pull new changes, migrate and install/update dependencies as necessary.

## Endpoints

### `/users`

#### `GET`

Returns a list of all users if authenticated as superuser, only yourself if otherwise.

#### `POST`

Registers a new user.

*Payload*

```
{
    'username': '<username_here>',
    'email': '<JrC_email_here>'
}
```

### `/login`

#### `POST`

Returns a token if username/password was valid, error message otherwise.

*Payload*

```
{
    'username': '<username_here>',
    'password': '<password_here>'
}
```

### `/check-token`

#### `POST`

Validates a token, returns userid on success, error message on failure.

*Payload*

```
{
    'token': '<token_here>'
}
```

### `/logout`

#### `POST`

Logs out the user.

*Payload*

```
{
    'token': '<token_here>'
}
```
