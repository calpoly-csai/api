# api

![GitHub repo size](https://img.shields.io/github/repo-size/calpoly-csai/api)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/calpoly-csai/api)
![GitHub closed issues](https://img.shields.io/github/issues-closed/calpoly-csai/api)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/calpoly-csai/api)

Official API for the [NIMBUS Voice Assistant](https://github.com/calpoly-csai/CSAI_Voice_Assistant) accessible via HTTP REST protocol.

## 🚧 This API is still in-development, so expect the endpoints to be constantly changing until finalized.

## GitHub Actions Status
![Deploy To Staging Server](https://github.com/calpoly-csai/api/workflows/Deploy%20Dev%20To%20Staging%20Server/badge.svg)

![Run Tests](https://github.com/calpoly-csai/api/workflows/Run%20Tests/badge.svg)

![Python PEP8 Style Check](https://github.com/calpoly-csai/api/workflows/Python%20PEP8%20Style%20Check/badge.svg)

![Python Pyre Type Annotation Check](https://github.com/calpoly-csai/api/workflows/Python%20Pyre%20Type%20Annotation%20Check/badge.svg)

## Documentation

- [ ] **TODO: INSERT LINK TO API DOCUMENTATION**

- [ ] **TODO: USE http://readthedocs.org to host the docs live on the internet**

- [ ] **TODO: [CREATE API DOCS 😅](https://github.com/calpoly-csai/api/milestone/2)**


## Dev Environment Setup
### Prerequisites
1. Python 3.6.9

2. pip 9.0.1


### Database Configuration

**Create a file** called `config.json` that should include at least the following details of a MySQL database:
```json
{
    ...
    "mysql": {
        "host": "HOSTNAME",
        "port": "PORT e.g. 3306",
        "user": "USERNAME",
        "password": "PASSWORD",
        "database": "DATABASE",
        ...
    }
    ...
}
```

**You can also use [`config_SAMPLE.json`](https://github.com/calpoly-csai/api/blob/dev/config_SAMPLE.json) as a reference**

_Contact anyone on the Data Team to get connection details for the Nimbus database_


### Install

```bash
pip3 install -r requirements.txt
```

### Run the API server

```bash
python3 nimbus_api.py
```

**_Run in the background_**
```bash
python3 nimbus_api.py&
```

### Run the tests
```bash
pytest
```

### Python PEP8 Style Standards
**_Run the `format` script to automatically make our code look nice_**
```bash
./format.sh
```

_Sometimes the format script is not enough, so run `lint` to manually style our code_
```bash
./lint.sh
```

## Deployment
### What we use
A Linux server (e.g. Ubuntu 18.04.3 LTS) with open firewall at `tcp:5000` for _Flask_, `tcp:80` for _http_ and `tcp:443` for _https_ and `tcp:22` for _ssh_ and `tcp:3306` for _mysql_

[See this documentation of the database deployment process](https://github.com/calpoly-csai/wiki/wiki/How-To-Install-and-Set-Up-a-Remote-MySQL-5.7-Database-and-Python-3.6-on-Ubuntu-18.04-with-Google-Cloud-Platform)


## Contributing
![GitHub issues](https://img.shields.io/github/issues/calpoly-csai/api)

Have a [**look at the v1.0 project board for TODOs**](https://github.com/calpoly-csai/api/projects/1)!

If you are new to programming, then filter for the [**![good first issue](https://img.shields.io/github/labels/calpoly-csai/api/good%20first%20issue)** label](https://github.com/calpoly-csai/api/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22)

Pull requests are welcome.

For major changes, please [**open an issue**](https://github.com/calpoly-csai/api/issues/new) first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)


## Authors and acknowledgment

[Michael Fekadu](https://www.github.com/mfekadu)

[John Waidhofer](https://www.github.com/Waidhoferj)

[Miles Aikens](https://www.github.com/snekiam)

[Daniel DeFoe](https://www.github.com/danield2255)

[Taylor Nguyen](https://www.github.com/taylor-nguyen-987)

[Adam Perlin](https://www.github.com/adamperlin)

[Simon Ibssa](https://www.github.com/ibssasimon)

[Kush Upadhyay](https://www.github.com/kpu-21)

[Ben Dahlgren](https://www.github.com/Dahlgreb)

[Tyler Campanile](https://www.github.com/tecampani)

[Steven Bradley](https://www.github.com/stbradle)
