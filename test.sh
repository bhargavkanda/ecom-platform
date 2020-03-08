#!/usr/bin/env bash
for i in drip zapuser account address zap_catalogue marketing zap_upload onboarding zap_admin discover payment cart coupon order referral zap_notification logistics offer zap_search zap_analytics extra_modules blog;do
 # if ! [[ ${array[i]} == *"__init"* ]]
  #then
    echo $i
    python manage.py makemigrations --empty $i
    #python manage.py migrate
    #rm -r zap_apps/$i/migrations
  #fi
done
