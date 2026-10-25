"""Offline regressions for import safeguards and non-destructive link reporting."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from import_medium import Content, stage, apply
from check_blog_links import classify, run

FEED = '''<rss xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><item><title>A new article</title><link>https://levelup.gitconnected.com/a-new-article-abcdef123456</link><pubDate>Mon, 03 Aug 2026 15:29:25 GMT</pubDate><category>Android</category><content:encoded><![CDATA[<figure><img src="https://example.com/image.png"></figure><p>WORDS</p>EMBED]]></content:encoded></item></channel></rss>'''.replace('WORDS','Useful published article text. '*45)

class MaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'data').mkdir();(self.root/'articles').mkdir()
        (self.root/'data/articles.json').write_text('[]\n');self.output=self.root/'review'
    def test_import_review_apply_and_deduplication(self):
        manifest=stage(self.root, FEED.replace('EMBED',''), self.output)
        self.assertEqual(len(manifest['candidates']),1)
        self.assertEqual(json.loads((self.root/'data/articles.json').read_text()),[])
        with self.assertRaisesRegex(ValueError,'needs review'):apply(self.root,self.output)
        manifest['candidates'][0]['reviewed']=True
        (self.output/'manifest.json').write_text(json.dumps(manifest))
        self.assertEqual(apply(self.root,self.output),1)
        self.assertEqual(apply(self.root,self.output),0)
        staged=stage(self.root,FEED.replace('EMBED',''),self.root/'next-review')
        self.assertEqual(staged['candidates'],[])
        with self.assertRaisesRegex(ValueError,'not empty'):stage(self.root,FEED,self.output)
    def test_embeds_block_apply_and_existing_files_are_preserved(self):
        m=stage(self.root,FEED.replace('EMBED','<iframe src=""><a href="https://medium.com/media/123/href">code</a></iframe>'),self.output)
        row=m['candidates'][0];self.assertTrue(row['issues']);row['reviewed']=True
        (self.output/'manifest.json').write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError,'needs review'):apply(self.root,self.output)
        row['issues']=[];(self.output/'manifest.json').write_text(json.dumps(m))
        target=self.root/'articles/a-new-article.html';target.write_text('Existing unindexed work')
        with self.assertRaisesRegex(ValueError,'overwrite'):apply(self.root,self.output)
        self.assertEqual(target.read_text(),'Existing unindexed work')
    def test_sanitise_markup_without_losing_code(self):
        c=Content('<script>alert(1)</script><p onclick="bad()">Hello <a href="javascript:bad()">world</a></p><pre><code>if (a &lt; b) return;</code></pre><img src="https://medium.com/_/stat?x=1"><script src="https://gist.github.com/example.js"></script>')
        text=''.join(c.output)
        self.assertNotIn('script',text);self.assertNotIn('onclick',text);self.assertNotIn('javascript:',text);self.assertNotIn('/_/stat',text)
        self.assertIn('if (a &lt; b) return;',text);self.assertTrue(c.issues)
    def test_link_classification(self):
        self.assertEqual(classify(200,'<title>404: Page Not Found | Mailchimp</title>'),'soft_404')
        self.assertEqual(classify(200,'<title>Kotlin Weekly #404</title>'),'ok')
        self.assertEqual(classify(403,'Forbidden'),'access_limited')
        self.assertEqual(classify(200,'<title>Kotlin Weekly #514</title>'),'ok')
    def test_report_keeps_links_and_drafts_only_missing_publisher_pages(self):
        data=[{'url':'/articles/a.html','title':'A','featured_in':[{'name':'Kotlin Weekly','url':'https://example.com/missing'},{'name':'Android Weekly','url':'https://example.com/blocked'}]}]
        file=self.root/'data/articles.json';file.write_text(json.dumps(data));before=file.read_bytes()
        def fake(url,timeout):return (404 if url.endswith('missing') else 403,url,'missing')
        with patch('check_blog_links.fetch',side_effect=fake):report=run(self.root,self.output)
        self.assertEqual(file.read_bytes(),before)
        self.assertIn('Kotlin Weekly',report['publisher_message_drafts'])
        self.assertNotIn('Android Weekly',report['publisher_message_drafts'])
        self.assertEqual(report['needs_review'],2)

if __name__=='__main__':unittest.main()
