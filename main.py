#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, jinja2, os, re
from google.appengine.ext import db
from models import Post

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class IndexHandler(BlogHandler):
    def render_index(self):
        self.render("index.html")

    def get(self):
        self.render_index()

class BlogMain(BlogHandler):
    def render_blog(self, title="", body="", error=""):
        posts = db.GqlQuery("SELECT * FROM Post "
                            "ORDER BY created DESC "
                            "LIMIT 5")

        self.render("blog.html", title=title, body=body, error=error, posts=posts)

    def get(self):
        self.render_blog()

class NewPostHandler(BlogHandler):

    def render_form(self, title="", body="", error=""):
        """ Render the new post form with or without an error, based on parameters """
        self.render("newpost.html", title=title, body=body, error=error)

    def get(self):
        self.render_form()
        #self.render("newpost.html", title, body, error)
    def post(self):
        """ Create a new blog post if possible. Otherwise, return with an error message """
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:

            # create a new Post object and store it in the database
            post = Post(
                title=title,
                body=body
                )
            post.put()

            # get the id of the new post, so we can render the post's page (via the permalink)
            id = post.key().id()
            self.redirect("/blog/%s" % id)
        else:
            error = "we need both a title and a body!"
            #self.render_form(title, body, error)
            self.render("newpost.html", title, body, error)

class ViewPostHandler(BlogHandler):

    def get(self, id):
        """ Render a page with post determined by the id (via the URL/permalink) """

        post = Post.get_by_id(int(id))
        if post:
            #t = jinja_env.get_template("post.html")
            #response = t.render(post=post)
            self.render("post.html", post=post)
        else:
            error = "there is no post with id %s" % id
            #t = jinja_env.get_template("404.html")
            #response = t.render(error=error)
            self.render("404.html", error=error)
        #self.response.out.write(response)

app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/blog/?', BlogMain),
    ('/blog/newpost', NewPostHandler),
    ('/blog/([0-9]+)', ViewPostHandler)
], debug=True)
