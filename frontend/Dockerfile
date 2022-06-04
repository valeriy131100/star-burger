FROM node:18.2-alpine
RUN mkdir /code
WORKDIR /code

COPY ./ /code
RUN npm install -g parcel@2.0.0-beta.2
RUN npm ci --include=dev

RUN parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
