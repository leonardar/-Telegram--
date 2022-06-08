from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTPDataError

from jinja2 import Template

from data.config import FROM_EMAIL, PASSWORD
from utils import get_logger

logger = get_logger(__name__)


async def sending_message(to_email: str, secret_key: str) -> None:
    """
    Функция отправляет письмо на почту пользователю,
    которую он ввел в чат боте.

    :param to_email: электронная почта
    :type to_email: str

    :param secret_key: секретный ключ
    :type secret_key: str

    :return: None
    :rtype: NoneType
    """

    try:
        with open(file="services/index.html", mode="r") as mail_template:
            template_new = Template(
                mail_template.read()
            ).render(secret_key=secret_key)
        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = "Регистрация"
        msg.attach(MIMEText(template_new, "html"))
        server = SMTP(host="smtp.yandex.ru", port=587)
        server.set_debuglevel(False)
        server.starttls()
        server.login(user=FROM_EMAIL, password=PASSWORD)
        server.send_message(msg=msg)
        server.quit()
    except SMTPDataError:
        pass
    except Exception as e:
        logger.error(e)
