FROM node:18.2-alpine
RUN mkdir /code
WORKDIR /code

COPY ./ /code
RUN npm ci --include=dev

RUN parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
