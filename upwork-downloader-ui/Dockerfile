FROM node:12

WORKDIR /code

COPY ./package.json .

RUN npm install

COPY ./tailwind.config.js .
COPY ./src ./src
COPY ./public ./public

CMD [ "npm", "run", "both" ] 
