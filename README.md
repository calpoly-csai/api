# api

![GitHub repo size](https://img.shields.io/github/repo-size/calpoly-csai/api)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/calpoly-csai/api)

![GitHub closed issues](https://img.shields.io/github/issues-closed/calpoly-csai/api)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/calpoly-csai/api)

![Python Version](https://img.shields.io/badge/python-3.6.9-blue)
![Pip Version](https://img.shields.io/badge/pip-9.0.1-blue)
![Ubuntu Version](https://img.shields.io/badge/ubuntu-18.04.3%20LTS-blue)
![MySQL Version](https://img.shields.io/badge/mysql-5.7.28-blue)
![GitHub Licence](https://img.shields.io/github/license/calpoly-csai/api)

Official API for the [NIMBUS Voice Assistant](https://github.com/calpoly-csai/CSAI_Voice_Assistant) accessible via HTTP REST protocol.

## 🚧 This API is still in-development, so expect the endpoints to be constantly changing until finalized.

## Documentation

- [ ] **TODO: INSERT LINK TO API DOCUMENTATION**

- [ ] **TODO: USE http://readthedocs.org to host the docs live on the internet**

- [ ] **TODO: [CREATE API DOCS 😅](https://github.com/calpoly-csai/api/milestone/2)**


## Dev Environment Setup
### Prerequisites
1. Python 3.6.9

2. pip 9.0.1

3. (_for deployment_) A Linux server (e.g. Ubuntu 18.04.3 LTS) with open firewall at `tcp:5000` for _Flask_, `tcp:80` for _http_ and `tcp:443` for _https_ and `tcp:22` for _ssh_ and `tcp:3306` for _mysql_

4. The _hostname_, _username_, and _password_ of a MySQL database (e.g. MySQL 5.7.28) inputted into `config.json`


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


## Contributing
![GitHub issues](https://img.shields.io/github/issues/calpoly-csai/api)

Have a [**look through the open issues**](https://github.com/calpoly-csai/api/issues)! 

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

[Adam Perlin](https://www.github.com/adamperlin)

[Simon Ibssa](https://www.github.com/ibssasimon)

[Kush Upadhyay](https://www.github.com/kpu-21)

[Ben Dahlgren](https://www.github.com/Dahlgreb)

[Tyler Campanile](https://www.github.com/tecampani)

[Steven Bradley](https://www.github.com/stbradle)
