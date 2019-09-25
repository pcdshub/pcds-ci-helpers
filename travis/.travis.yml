language: python
dist: xenial
python: 3.7

env:
  global:
    # Doctr deploy key for pcdshub/lcls-plc-kfe-gmd-vac
    - secure: "R/SYgFK1SBIk783FFvAGXgBxap0sJcDtnCIwAAdhQZt1IWCkBMaIPmszkl6XvL3V7SS6/yRsxgYStVlDJ6aOZ4pRMQVW7ckv0h0LVXKYzoT5epc8Ji8sNsukto2aXOfPXukWRLaPRhCZtLNCovq+Lp3YXmHgcZIA42zp11/XwPcLJ7rA/VA2lUn8cr5KbyRGYQ0afLhS2u8HdkqDSDynjcbqkyzpcrBWe2HvSmMOFarovQkmmAFJr3tIIpTIhq2CYeVbKLhT8Avuxw9BAwK86NlzT2ph9HoVcyqAfMoqTzuQNMcUISUPH+nIg9FlT4C4B8BjuAw5A4V0WQDtHNTKsRp++xmlWT7FAJW0yTGdArkoNNCTtfKMgFS8v9NlKjVe/rCEpmCU6/wCDsJQUQT0yd+imPL3jjn3O1KGZocYe0zpPohu+bhvg/d0dWRCdZZ+Y8duefHCx7xyvOzuf5ceRRKDNMqTf75T8HZJ6T+uKjOnqArH+HUGuzoqmgpwPyboDBCGpRtpJ5Hue9G/9iOEeCGQg2KHFcTU2GOopH93chEMIBKCpIZrlzvSr15ZWO72/Clike/PQiQQ+Kad43mDKlLk5uYNT72pGerALqhuR1A6BXmQgwQn9fDVO8b2SsHSlpQcBNO+n5EohypFFLxLSKSTffLdHo5+xZPVvJkyNLI="

install:
  # pytmc
  - pip install Jinja2 lxml
  - pip install git+https://github.com/slaclab/pytmc.git@v2.1.0
  - pip install git+https://github.com/epicsdeb/pypdb.git

  # docs
  - pip install sphinx recommonmark

script:
  - |
    find plc -name '*.tsproj' -print0 | 
        while IFS= read -r -d '' tsproj; do 
            pytmc pragmalint --verbose "$tsproj";
            pytmc summary --all --code "$tsproj" > docs/source/$(basename $tsproj).md;
        done

  - |
    find plc -name '*.tmc' -print0 |
        while IFS= read -r -d '' tmc; do
            db_filename=docs/source/$(basename $tmc).db
            db_errors=$(( ( pytmc db --allow-errors "$tmc") 1>$db_filename) 2>&1)
            md_filename=docs/source/$(basename $tmc).md

            (
                echo "$(basename $tmc)"
                echo "=================="
                echo ""

                if [ ! -z "$db_errors" ]; then
                    echo "Errors"
                    echo "------"
                    echo '```'
                    echo "$db_errors"
                    echo '```'
                    echo ""
                fi

                echo "Records"
                echo "-------"
                echo '```'
                grep "^record" $db_filename | sed -e 's/^record(\(.*\),\(.*\)).*$/\2 (\1)/' | sort
                echo '```'
                echo ""

                echo "EPICS database"
                echo "--------------"
                echo '```'
                cat $db_filename
                echo '```'
            ) > $md_filename
        done

  - pushd docs
  - make html
  - popd

  # Deploy the latest version of the docs with doctr
  - pip install doctr
  - doctr deploy . --built-docs docs/build/html --deploy-branch-name gh-pages --command "touch .nojekyll; git add .nojekyll" --no-require-master
