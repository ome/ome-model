SPHINX_THEME=sphinxdoc

all: html

html:
	mvn -Dsphinx.builder=html -Dsphinx.theme=$(SPHINX_THEME)

linkcheck:
	mvn -Dsphinx.builder=linkcheck -Dsphinx.theme=$(SPHINX_THEME)

clean:
	mvn clean
