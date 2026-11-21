# pageskip

![python-version](https://img.shields.io/badge/3.13-a?style=for-the-badge&logo=python&logoColor=%23ffffff&label=python&labelColor=%233772a3&color=%23555555) ![nix-version](https://img.shields.io/badge/unstable-a?style=for-the-badge&logo=nixos&logoColor=%23ffffff&label=Nix&labelColor=%237bb6e1&color=%23555555&link=https%3A%2F%2Fnixos.org%2F)

This project aims to add lexical search to [EPSEVG][epsevg]'s [STIC][stic]
working group's [ticket system][gn6].

### Motivation
The ticket website lacks a way to search for tickets by their text contents. The
only way to find tickets is to sift through often non-descriptive titles and
skip through page after page of ticket listings.

In the [REIN][rein] subject, we're tasked with building an open ended project
related to the things learnt in the subject. As an intern at STIC, since I
often struggle with finding tickets, I decided to build this tool.

This project is based on an authenticated spider that retrieves all tickets and
indexes several relevant fields on elasticsearch.

## Setup
This project uses Nix to manage dependencies and virtual environments. To enter
the developement environment, run:
```bash
nix develop
```

## Run
You can start the spider with the following command:
```
scrapy crawl pageskip_spider
```

> [!IMPORTANT]
> Note that you'll have to run the spider on a graphical session, since
> the authentication process involves opening a browser window with
> [UPC's login page][login] where you'll have to authenticate.

> [!TIP]
> Only users authorized to access the ticket dashboards will be able to run the
> spider.

[epsevg]: https://epsevg.upc.edu
[stic]: https://epsevg.upc.edu/ca/escola/que-necessites
[gn6]: https://gn6.upc.edu/epsevg
[rein]: https://www.upc.edu/grau/guiadocent/cat/340455/recuperacio-de-la-informacio.pdf
[login]: https://login.upc.edu
