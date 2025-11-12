try:
    import google
    google.__path__.append('/root/onl-bf-sde/build/pkgsrc/bf-drivers/third-party/python_out/google')
except Exception as e:
    pass
