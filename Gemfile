# frozen_string_literal: true

source "https://rubygems.org"

# Pinned deliberately. `lint` and `push` did not exist before 0.9.0, and an
# unpinned install silently resolves to 0.3.2, which has only build/serve/
# version — that is what kept CI red and stopped the repo ever pushing to TRMNL.
#
# Installed through Bundler rather than `gem install` because trmnl_preview
# needs cgi ~> 0.5, while Ruby 3.4 ships cgi 0.4.x as an already-activated
# default gem. RubyGems cannot resolve that upgrade and dies inside its own
# conflict reporter ("undefined method 'request' for nil"), which hides the
# real cause. Bundler resolves it correctly.
gem "trmnl_preview", "~> 0.11"
