# Python Works with Nest Sample App


NOTE: This is not an official Google product.

## 1. Introduction

This is a simple web app that talks to the Works with Nest API using Python and  
the Flask web framework. You'll use a Nest product to be accessed from the app.  
   
—————————————————————————————————————

## 2. Requirements

* The sample code
* Basic knowledge of HTML, CSS, Javascript, and Python (to change the sample)
* Python interpreter 2.7.x
* At least one Nest device, such as Nest Thermostat, Nest Cam, or Nest Protect

—————————————————————————————————————

<a name="install"> </a>
## 3. Install dependencies

This README uses Python's PIP to manage dependent packages.  If you prefer to use Docker  
instead, follow the instructions in [README-Docker.md](README-Docker.md).

1. Install PIP and Python 2.7: 
   [https://zaiste.net/posts/installing\_python\_27\_on\_osx\_with\_homebrew/](https://zaiste.net/posts/installing_python_27_on_osx_with_homebrew/)<br/>
1. Clone or download this sample code.  You can modify it to use these options:
   * (Optional) Use Redis sessions  
     You can use Redis for Flask server-side sessions instead of the default Flask cookie based sessions.
     *  Install Redis for your environment: [https://redis.io](http://redis.io)
     *  Uncomment `redis` in requirements.txt.
   * (Optional) Use REST streaming  
     You can use REST Streaming server-sent events instead of polling the API server.  
     *  Update static/js/app.js and un-comment `listenRESTStreamClient()`.  Comment out `pollRESTClient()`.  
     *  Uncomment `sseclient-py` and `urllib3` in requirements.txt.<br/><br/>
1. In a terminal window, go to the nest-python directory and run the following
commands.
 
Spin up a virtual environment:  
```
$ pip install virtualenv
$ virtualenv env
$ . env/bin/activate
```

Install the dependencies in the virtual environment: 
```
(env) $ pip install -r requirements.txt
```

—————————————————————————————————————

## 4. Set up your Nest device

If you don't already have a Nest device set up and associated with your  
home.nest.com account, use one of the following procedures.

Set up a Nest device with a Mac or Windows computer

-OR-

Set up a Nest device with the Nest App

-OR- 

Use the Nest Home Simulator to simulate a Nest device

—————————————————————————————————————

## 5. Create a Nest OAuth Client at console.developers.nest.com

Use the same account that you used for your Nest device. 

For the redirect URI, use http://localhost:5000/callback

For the permissions, select read/write corresponding with your Nest client. For 
example,  
if your Nest product is a Thermostat, select Thermostat Read/Write.

The next step is to set your OAuth client ID and client secret as environment  
variables so these values can be retrieved by the application to authorize 
your Nest integration.

If you are using Linux or MacOS, open a Bash shell and type the commands below  
(substitute your client ID and secret you copied from your client page):

```
$ export PRODUCT_ID='Your OAuth client ID here'
$ export PRODUCT_SECRET='Your OAuth client secret here'
```

—————————————————————————————————————

## 6. Run the app

If it's not already running, spin up the virtual environment in your nest-python directory:


```
$ . env/bin/activate
```

Run app.py:


```
(env) $ python app.py
``` 

<br/><br/>
**(Optional) Use Redis sessions**  
* Verify you have the redis server installed in the [Install dependencies](#install) section.
* Open another terminal window and start the redis server:
```
$ redis-server
```
After starting redis, run app.py (with Redis server-side sessions) in your nest-python directory:
```
(env) $ python app.py --use-redis
```  
<br/>


If you are prompted, click to allow incoming network connections.

—————————————————————————————————————

## 7. Open http://localhost:5000/

Click **Login**.

When you log in, you are redirected to the Nest Authorization screen.  
On the Nest Authorization screen, click **Accept**.

When you accept the integration, the Nest Authorization screen redirects to the  
Redirect URL configured for your Nest client integration
(http://localhost:5000/callback).

—————————————————————————————————————

## 8. See the app in a mobile format

In Chrome, right-click the app and select **Inspect**.  
Click the icon that looks like a phone (**Toggle device toolbar**).  
In the emulated devices menu, select another format, such as iPhone 6.

## Companion codelab

[10 Tips for a successful Nest
integration](https://codelabs.developers.google.com/codelabs/nest-ten-tips-for-success)
   
## Contributing

Contributions are always welcome and highly encouraged.

See [CONTRIBUTING](CONTRIBUTING.md) for more information on how to get started.

## License

Apache 2.0 - See [LICENSE](LICENSE) for more information.
