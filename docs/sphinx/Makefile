SPHINX_THEME=sphinxdoc

all: html

html:
	mvn -Dsphinx.builder=html -Dsphinx.html.theme=$(SPHINX_THEME)

linkcheck:
	mvn -Dsphinx.builder=linkcheck

clean:
	mvn clean
