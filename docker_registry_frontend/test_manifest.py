import json
from unittest import TestCase

from docker_registry_frontend.manifest import DockerRegistrySchema1Manifest

docker_registry_schema1_manifest_content = """{
   "schemaVersion": 1,
   "name": "registry",
   "tag": "2",
   "architecture": "amd64",
   "fsLayers": [
      {
         "blobSum": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4"
      },
      {
         "blobSum": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4"
      },
      {
         "blobSum": "sha256:80702e2b70f61359e1e2960e3376e7720114ecadd81462129c0902dbbc13f9ae"
      },
      {
         "blobSum": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4"
      },
      {
         "blobSum": "sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4"
      },
      {
         "blobSum": "sha256:b02e22b09c928cb73d056c64f5c30a2146ba64a306a0feb32e9519ad9fcade85"
      },
      {
         "blobSum": "sha256:4ab866128436778ccad5876ffacf2db98d396ba0a2cec7069d30480b1dd09d7d"
      },
      {
         "blobSum": "sha256:bb9291d659e1f09866690763bfd9be24b4c9045945c4422dad24c11892cb06a4"
      },
      {
         "blobSum": "sha256:12a7970a6783dc60e319ae3477ce11dc2a9c845a6ff3ac9a05820042245f08b6"
      }
   ],
   "history": [
      {
         "v1Compatibility": "{\\"architecture\\":\\"amd64\\",\\"config\\":{\\"Hostname\\":\\"837a64dcc771\\",\\"Domainname\\":\\"\\",\\"User\\":\\"\\",\\"AttachStdin\\":false,\\"AttachStdout\\":false,\\"AttachStderr\\":false,\\"ExposedPorts\\":{\\"5000/tcp\\":{}},\\"Tty\\":false,\\"OpenStdin\\":false,\\"StdinOnce\\":false,\\"Env\\":[\\"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\\"],\\"Cmd\\":[\\"/etc/docker/registry/config.yml\\"],\\"Image\\":\\"sha256:6c66860152e62b34b4b74c1231f361974f916cce83ea98ddc8594f139e034e97\\",\\"Volumes\\":{\\"/var/lib/registry\\":{}},\\"WorkingDir\\":\\"\\",\\"Entrypoint\\":[\\"/entrypoint.sh\\"],\\"OnBuild\\":[],\\"Labels\\":{}},\\"container\\":\\"e499047a6253a7176cf714b0ef1cad258ab1a3a309a7aa28659d46b0a7cba85b\\",\\"container_config\\":{\\"Hostname\\":\\"837a64dcc771\\",\\"Domainname\\":\\"\\",\\"User\\":\\"\\",\\"AttachStdin\\":false,\\"AttachStdout\\":false,\\"AttachStderr\\":false,\\"ExposedPorts\\":{\\"5000/tcp\\":{}},\\"Tty\\":false,\\"OpenStdin\\":false,\\"StdinOnce\\":false,\\"Env\\":[\\"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\\"],\\"Cmd\\":[\\"/bin/sh\\",\\"-c\\",\\"#(nop) \\",\\"CMD [\\\\\\"/etc/docker/registry/config.yml\\\\\\"]\\"],\\"Image\\":\\"sha256:6c66860152e62b34b4b74c1231f361974f916cce83ea98ddc8594f139e034e97\\",\\"Volumes\\":{\\"/var/lib/registry\\":{}},\\"WorkingDir\\":\\"\\",\\"Entrypoint\\":[\\"/entrypoint.sh\\"],\\"OnBuild\\":[],\\"Labels\\":{}},\\"created\\":\\"2017-04-06T16:15:54.391896801Z\\",\\"docker_version\\":\\"1.12.6\\",\\"id\\":\\"e80288d8b7a1c986005f057600255ace19b9b848b2a1a0299d94b21ab6e90c9e\\",\\"os\\":\\"linux\\",\\"parent\\":\\"7a3b405b02ea3717b33b73240d5aaab4fe976daf5983010dfae3926a306a1beb\\",\\"throwaway\\":true}"
      },
      {
         "v1Compatibility": "{\\"id\\":\\"7a3b405b02ea3717b33b73240d5aaab4fe976daf5983010dfae3926a306a1beb\\",\\"parent\\":\\"2e015847eedab73a2ee515664db7ac8533acc638a2283b5ca741a2d9e9cf9a02\\",\\"created\\":\\"2017-04-06T16:15:54.095800009Z\\",\\"container_config\\":{\\"Cmd\\":[\\"/bin/sh -c #(nop)  ENTRYPOINT [\\\\\\"/entrypoint.sh\\\\\\"]\\"]},\\"throwaway\\":true}"
      },
      {
         "v1Compatibility": "{\\"id\\":\\"2e015847eedab73a2ee515664db7ac8533acc638a2283b5ca741a2d9e9cf9a02\\",\\"parent\\":\\"b2f9b231ab40640643c501df498fb258d53c166dca7882a350d785a963200c8d\\",\\"created\\":\\"2017-04-06T16:15:53.792327987Z\\",\\"container_config\\":{\\"Cmd\\":[\\"/bin/sh -c #(nop) COPY file:7b57f7ab1a8cf85c00768560fffc926543a60c9c9f7a2b172767dcc9a3203394 in /entrypoint.sh \\"]}}"
      },
      {
         "v1Compatibility": "{\\"id\\":\\"b2f9b231ab40640643c501df498fb258d53c166dca7882a350d785a963200c8d\\",\\"parent\\":\\"2758b09e474717288eb2fa935f8d66ff2bfeb9e6bcd2d5385be57058566f3e82\\",\\"created\\":\\"2017-04-06T16:15:53.227780712Z\\",\\"container_config\\":{\\"Cmd\\":[\\"/bin/sh -c #(nop)  EXPOSE 5000/tcp\\"]},\\"throwaway\\":true}"
      },
      {
         "v1Compatibility": "{\\"id\\":\\"2758b09e474717288eb2fa935f8d66ff2bfeb9e6bcd2d5385be57058566f3e82\\",\\"parent\\":\\"da8f176cb9465bdb6de6bf44acbe4f2959e1cefe46bd4cf6d1d6ece59af4fd01\\",\\"created\\":\\"2017-04-06T16:15:52.89982671Z\\",\\"container_config\\":{\\"Cmd\\":[\\"/bin/sh -c #(nop)  VOLUME [/var/lib/registry]\\"]},\\"throwaway\\":true}"
      },
      {
         "v1Compatibility": "{\\"id\\":\\"da8f176cb9465bdb6de6bf44acbe4f2959e1cefe46bd4cf6d1d6ece59af4fd01\\",\\"parent\\":\\"67e86c19d7b4d204e1c3fe6b8f06ae5f86657cb239b4b003301a57c9caa8ee86\\",\\"created\\":\\"2017-04-06T16:15:52.538750737Z\\",\\"container_config\\":{\\"Cmd\\":[\\"/bin/sh -c #(nop) COPY file:6c4758d509045dc45381fa2df2e7ffcc661afcaa29805c75f8f1976f2b016db8 in /etc/docker/registry/config.yml \\"]}}"
      },
      {
         "v1Compatibility": "{\\"id\\":\\"67e86c19d7b4d204e1c3fe6b8f06ae5f86657cb239b4b003301a57c9caa8ee86\\",\\"parent\\":\\"5b11ee0d7bafa77114d2a1b2c868d79cb215a52791c530a962415bb221575dd5\\",\\"created\\":\\"2017-04-06T16:15:52.03445189Z\\",\\"container_config\\":{\\"Cmd\\":[\\"/bin/sh -c #(nop) COPY file:286222b32843a33f78b8d717455a70255082b971db4fc53d46d467d2526359ab in /bin/registry \\"]}}"
      },
      {
         "v1Compatibility": "{\\"id\\":\\"5b11ee0d7bafa77114d2a1b2c868d79cb215a52791c530a962415bb221575dd5\\",\\"parent\\":\\"90b72de51218d63a90000f776271067e78b4c9c2114e6d76d79e6df3ad68a440\\",\\"created\\":\\"2017-03-03T23:33:54.047862762Z\\",\\"container_config\\":{\\"Cmd\\":[\\"/bin/sh -c set -ex     \\\\u0026\\\\u0026 apk add --no-cache ca-certificates apache2-utils\\"]}}"
      },
      {
         "v1Compatibility": "{\\"id\\":\\"90b72de51218d63a90000f776271067e78b4c9c2114e6d76d79e6df3ad68a440\\",\\"created\\":\\"2017-03-03T20:32:21.010554522Z\\",\\"container_config\\":{\\"Cmd\\":[\\"/bin/sh -c #(nop) ADD file:3df55c321c1c8d73f22bc69240c0764290d6cb293da46ba8f94ed25473fb5853 in / \\"]}}"
      }
   ],
   "signatures": [
      {
         "header": {
            "jwk": {
               "crv": "P-256",
               "kid": "X4PF:AXHS:XSBP:5TXF:WDNJ:O4KX:5DGY:SCXM:SZCW:TRVD:WGWC:RPLK",
               "kty": "EC",
               "x": "Osl2ppaIzS2FWWu8dVrFfxIol-2L5NkkJhM8zbxxc_A",
               "y": "WJfjmG_vICKN_rUKTYpncHfzg8EB8aj9-FcTct6-zuY"
            },
            "alg": "ES256"
         },
         "signature": "_1-NY-FEOhfezEE7AeyjC7assgaNkJ_4ScjGIOdc6B-OCyXWJPoU4I3P_j5qjMGnmbC47NYRE-cixCRk4XB2EA",
         "protected": "eyJmb3JtYXRMZW5ndGgiOjU3MTQsImZvcm1hdFRhaWwiOiJDbjAiLCJ0aW1lIjoiMjAxNy0wNS0xMVQyMToxOToyN1oifQ"
      }
   ]
}"""


class TestDockerRegistryManifest:
    def test_get_created_date(self):
        self.assertEqual(
            self.manifest.get_created_date(),
            '2017-04-06T16:15:54.391896801Z'
        )

    def test_get_docker_version(self):
        self.assertEqual(
            self.manifest.get_docker_version(),
            '1.12.6'
        )

    def test_get_entrypoint(self):
        self.assertEqual(
            self.manifest.get_entrypoint(),
            ['/entrypoint.sh']
        )

    def test_get_exposed_ports(self):
        self.assertEqual(
            self.manifest.get_exposed_ports(),
            {'5000/tcp': {}}
        )

    def test_get_volumes(self):
        self.assertEqual(
            self.manifest.get_volumes(),
            {'/var/lib/registry': {}}
        )


class TestDockerRegistrySchema1Manifest(TestCase, TestDockerRegistryManifest):
    def setUp(self):
        self.manifest = DockerRegistrySchema1Manifest(
            json.loads(docker_registry_schema1_manifest_content)
        )
