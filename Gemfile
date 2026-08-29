# frozen_string_literal: true

source "https://rubygems.org"

# Pinned deliberately. `lint` and `push` did not exist before 0.9.0, and an
# unpinned install silently resolves to 0.3.2, which has only build/serve/
# version — that is what kept CI red and stopped the repo ever pushing to TRMNL.
#
# Installed through Bundler rather than `gem install` because the real
# constraint is invisible otherwise: trmnl_preview 0.11.0 advertises
# `ruby >= 3.4`, but depends on trmnl-liquid ~> 0.7.0, and every trmnl-liquid
# from 0.5.0 up needs `ruby >= 4.0`. On Ruby 3.4 `gem install` crashes inside
# its own conflict reporter ("undefined method 'request' for nil") and never
# names the cause. Bundler prints the chain. CI pins ruby-version 4.0 to match.
gem "trmnl_preview", "~> 0.11"
