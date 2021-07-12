FROM python
WORKDIR '/coin'
COPY . .
RUN pip install -r requirements.txt
CMD python blockchain.py
