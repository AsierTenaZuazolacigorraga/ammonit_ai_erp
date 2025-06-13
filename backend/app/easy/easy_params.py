import os

from dotenv import load_dotenv

load_dotenv()

IS_LOCAL = True

OUTLOOK_ID = os.getenv("OUTLOOK_ID")
OUTLOOK_SECRET = os.getenv("OUTLOOK_SECRET")

EMAIL = "asier.tena.zu@outlook.com"
# EMAIL = "alberdi.autom@outlook.com"
# EMAIL = "asier.tena.zu@ammonitammonit.onmicrosoft.com"


ORDER_1 = r"/home/atena/my_projects/iot_bind/.gitignores/Invoice 1/output1.pdf"
ORDER_2 = r"/home/atena/my_projects/iot_bind/.gitignores/Invoice 1/output2.pdf"
ORDER_3 = r"/home/atena/my_projects/iot_bind/.gitignores/Invoice 1/output3.pdf"
ORDER_4 = r"/home/atena/my_projects/iot_bind/.gitignores/Invoice 1/output4.pdf"
ORDER_danobat = (
    r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/DANOBAT/100083396.pdf"
)
ORDER_fagor = (
    r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/FAGOR/5B-20575.pdf"
)
ORDER_inola = r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/INOLA/87-25.pdf"
ORDER_matisa = (
    r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/MATISA/CF2503-87388.pdf"
)
ORDER_matisa2 = r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/MATISA/aaaaaaaaaaaaaaaaaaaaaaaa.pdf"
ORDER_ulma1 = r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/ULMA/598153.pdf"
ORDER_ulma2 = r"/home/atena/my_projects/iot_bind/.gitignores/Eskariak/ULMA/4595390.pdf"
ORDERS = [
    # ORDER_1,
    # ORDER_2,
    # ORDER_3,
    ORDER_4,
    ORDER_danobat,
    ORDER_fagor,
    ORDER_inola,
    ORDER_matisa,
    ORDER_ulma1,
    ORDER_ulma2,
]
