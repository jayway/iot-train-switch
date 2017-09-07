# AWS IoT switches

## Create environment

Install virtualenv:
```bash
pip install virtualenv
```

Create new environment:
```bash
mkdir switch && cd switch
virtualenv env
source env/bin/activate
pip install adafruit-pca9685
pip install AWSIoTPythonSDK
```

Download AWS IoT Thing certs (4 in total, including rootCA cert) to `cert` dir in `env`
