FROM node:16-alpine

WORKDIR /app

COPY package.json /app
COPY package-lock.json /app
RUN apk add --no-cache yarn \
    && yarn install --network-timeout 1000000\
    && yarn global add update-browserslist-db@latest
COPY . /app
CMD ["yarn", "start"]

