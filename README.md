# XFakturist

Minimalist stand-alone XRechnung generator


## Outline

When it comes to [**open-source**](https://opensource.org/osd) and [**stand-alone applications**](https://en.wikipedia.org/wiki/Standalone_software) capable of creating **XML electronic invoices**, there are not many options to chose from. **XFakturist** strives to be one of them, while focussing on simple invoices with a small number of invoice items. While **XFakturist** is a minimalist tool to issue electronic invoices, it features the embedding of invoice attachments, like PDF documents, in the XML data. As a command-line application with incomplete documentation, **XFakturist** will likely only appeal to the technically savvy computer user.


## Features

**XFakturist** is [free software](https://opensource.org/osd) that aims at creating [electronic invoices](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/What+is+eInvoicing) that comply with the [XRechnung](https://xeinkauf.de/xrechnung/) standard. [XRechnung](https://xeinkauf.de/xrechnung/) is a German [XML](https://en.wikipedia.org/wiki/XML)-based data format and semantic model (see the [XRechnung FAQ](https://en.e-rechnung-bund.de/e-invoicing-faq/xrechnung/)). The **XFakturist** software is stand-alone, running locally on your own computer: it does not depend on a network connection, API or similar third-party remote service. By not sending your invoice data to somewhere in the internet, **XFakturist** safeguards data privacy.

Currently, **XFakturist** is a simple but functional tool, mostly written in Python, and must be used from the command line. It does not include a graphical user interface. The software comprises a set of commands that can be executed, for example, in the [macOS Terminal](https://support.apple.com/en-gb/guide/terminal/trmld4c92d55/mac).

**XFakturist** comes **without any warranty**. You may use it at your own risk. In particular, users assume full responsibility for the correctness of invoice data and monetary amounts contained in the final XML file. Furthermore, creating an XML file with **XFakturist** does not automatically guarantee compliance with the [XRechnung](https://xeinkauf.de/xrechnung/) standard, as this also depends on the invoice data that you are feeding into the XML creation process.

Users may want to check compliance with third-party software, for example, by employing the stand-alone and open-source [validation and visualisation software](https://github.com/itplr-kosit) published by the German governments' [Coordination Office for IT Standards](https://www.xoev.de/) (KoSIT). **XFakturist** offers a simple installation method for these KoSIT tools as well as a basic command-line interface to use them.


## Project rationale

Until year 2024, freelancers and small businesses were accustomed to send invoices electronically to clients or customers, in the form of human readable PDF documents. [Tamper-proof and safely stored](https://ao.bundesfinanzministerium.de/ao/2023/Anhaenge/BMF-Schreiben-und-gleichlautende-Laendererlasse/Anhang-64/inhalt.html), and, if all legally required information was provided, such documents were sufficient for invoice recipients to claim input tax deduction. These PDF documents were easily created, using simple and freely available tools, and, were quickly sent by email.

Between 2025 and 2027, the German legal VAT framework will be adjusted, step-by-step, to gradually enforce mandatory [electronic invoicing](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/What+is+eInvoicing): after 2027, all German domestic business-to-business invoicing will have to be done by electronic (XML) data exchange. There are not many exceptions to this general rule. 

While traditional PDF invoices are easily issued with common tools, creating XML data that meet the legal requirements for _electronic invoicing_ is anything but simple. 

In late 2024, a wide range of commercial software solutions existed to generate XML electronic invoices. But many of them were too complex or expensive for the simple needs of small businesses. As an alternative, some free-of-charge web applications were available for the purpose at hand, sometimes requiring registration. At the same time, open-source and stand-alone software for electronic invoicing was rare. This observation motivated the creation of **XFakturist**.


## Usage

After a complete installation, three separate **XFakturist** terminal commands are available:

- 
  ```
  xr-compile invoice.xlsx
  ```
  reads invoice data from a suitably structured XLSX workbook `invoice.xlsx`. A template for such a workbook is file [`template.xlsx`](template.xlsx), found in the **XFakturist** top level directory. Copy and rename it to insert your own invoice data. Python script `xr-compile` is designed to create XML file `invoice.xml` and compilation log-file `invoice.log`.

-
  ```
  xr-validate invoice.xml
  ```
  runs the [KoSIT validator](https://github.com/itplr-kosit/validator) software for XML electronic invoices and creates two validation reports, `invoice_validation_report.xml` and `invoice_validation_report.html`.

-
  ```
  xr-convert invoice.xml
  ```
  runs the [KoSIT visualisation](https://github.com/itplr-kosit/xrechnung-visualization) software for XML electronic invoices and creates two documents that show invoice data in a human readable format. In the example given here, these documents would have the file names `invoice_converted_de.html` and `invoice_converted_de.pdf`. Field names in these documents are in German. To obtain English language field designations, add `en` as a second command-line parameter:
  ```
  xr-convert invoice.xml en
  ```


## Installation

_Currently, only macOS and Linux systems are supported. MS Windows might also work if the [Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install) or the [Git bash](https://git-scm.com/) are available._

### Python tool `xr-compile`

Python (version 3.10 or later) must be installed on your system, for example, a current [Anaconda distribution](https://www.anaconda.com/download). Among the required Python packages, we highlight the following ones, which might require upgrading your Python installation:
```
json5
xmltodict
```
XML electronic invoice creation using command `xr-compile` does only depend on the availability of such a Python installation on your computer. Download and unpack the **XFakturist** ZIP-file or clone the **XFakturist** Github repository. Make sure that Python script `xr-compile` is in your search path.

### KoSIT software installation

To run the [KoSIT validation and visualisation software](https://github.com/itplr-kosit), a recent version of a Java runtime environment is required, for example [Eclipse Temurin JRE](https://adoptium.net/de/temurin/releases/).

**XFakturist** offers the shell scripts `xr-validate` and `xr-convert` to run the [KoSIT software](https://github.com/itplr-kosit). Make sure that these scripts are in your search path. 

KoSIT software does not come prepackaged with **XFakturist**. It must be downloaded and installed separately. To simplify this installation process, **XFakturist** provides shell script `get-kosit-xr`. Run this script from the top-level **XFakturist** directory. It downloads and unpacks three different [KoSIT software packages](https://github.com/itplr-kosit) as well as two software dependencies, [Saxonica Saxon Home Edition](https://github.com/Saxonica/Saxon-HE/) and [Apache Formatting Objects Processor](https://xmlgraphics.apache.org/fop/). 

Four of these five packages are licensed by their respective vendors under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0.html). Software firm [Saxonica](https://www.saxonica.com/) also distributes its _Saxon Home Edition_ as [open source software](https://saxonica.plan.io/projects/saxonmirrorhe).

After running installation script `get-kosit-xr`, **XFakturist** shell scripts, `xr-validate` and `xr-convert`, should be functional.


## XRechnung standard

**This section represents our own interpretation of publicly available information. Be aware that it is neither legal nor tax advice**.

As of 1 January 2025, the German VAT Act ([Umsatzsteuergesetz](https://www.gesetze-im-internet.de/ustg_1980/index.html)) includes a [definition of an _electronic_ invoice](https://www.gesetze-im-internet.de/ustg_1980/__14.html): an invoice that is issued, transmitted and received in an electronic and structured data format. Such a format must facilitate automatic and electronic processing of invoice data. Compliance of an invoice with [European Union Directive 2014/55/EU](https://eur-lex.europa.eu/eli/dir/2014/55/oj/eng), which implicitly endorses the European standard [EN 16931](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/Obtaining+a+copy+of+the+European+standard+on+eInvoicing), will perhaps be the most common approach to satisfy the basic legal requirements of the German VAT Act. Note that the [XRechnung](https://xeinkauf.de/xrechnung/) standard builds on and extends European standard [EN 16931](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/Obtaining+a+copy+of+the+European+standard+on+eInvoicing).

In an [official announcement](https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Steuerarten/Umsatzsteuer/2024-10-15-einfuehrung-e-rechnung.html) of 15 October 2024, the Federal Ministry of Finance offered advice regarding the introduction of mandatory electronic invoicing of domestic business-to-business transactions, which started in Germany in 2025. The announcement states that, for VAT purposes, compliance with the [XRechnung](https://xeinkauf.de/xrechnung/) standard will classify respective XML data as an _electronic invoice_ in accordance with the law.

For that reason, **XFakturist** was designed to generate _electronic invoices_ that employ the [XRechnung](https://xeinkauf.de/xrechnung/) standard.


## License

**XFakturist** is subject to open-source software license [AGPL-3.0-only](https://opensource.org/license/agpl-v3), unless you have received this program directly from the author, Dr Tim Brunne (Munich), pursuant to the terms of a commercial license agreement with the author.
