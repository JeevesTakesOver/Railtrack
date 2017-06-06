with import <nixpkgs> {};
with pkgs.python27Packages;

stdenv.mkDerivation  { 
  name = "impurePythonEnv";
  buildInputs = [
    taglib
    openssl
    git
    libxml2
    libxslt
    libzip
    python27Full
    python27Packages.virtualenv
    python27Packages.pip
    stdenv
    zlib ];
  src = null;
  # When used as `nix-shell --pure`
  shellHook = ''
  PID=$$
  unset http_proxy
  export GIT_SSL_CAINFO=/etc/ssl/certs/ca-bundle.crt
   # set SOURCE_DATE_EPOCH so that we can use python wheels
   SOURCE_DATE_EPOCH=$(date +%s)
  virtualenv --no-setuptools /tmp/$PID/venv 
  wget -c https://bootstrap.pypa.io/get-pip.py
  /tmp/$PID/venv/bin/python get-pip.py
  /tmp/$PID/venv/bin/pip install -r requirements.txt 
  export PATH=/tmp/$PID/venv/bin:$PATH
  ln -s /tmp/$PID/venv venv
  '';
}
