#using node verison 22 that we uses in our frontend
FROM node:22

WORKDIR /

#copy package list fron workdir and set download destination to this folder
COPY package*.json ./

#download all dependencies
RUN npm install

#copy everything in the app into container
COPY . .

# # Switch to the built-in non-root "node" user
# USER node
# # Ensure the "node" user owns the application files
# RUN chown -R node:node /
 

ENV PORT=9000
EXPOSE 9000

CMD ["npm","run","dev", "--","--host","0.0.0.0"]
