def props
def VERSION
def FIX
def RELEASE

node {
   props = readProperties file:'props.txt'
   VERSION = props['version']
   FIX = props['fix']
   RELEASE = VERSION + "_" + FIX
}

pipeline {
   stages {
      stage('Build') {
         echo ${RELEASE}
      }
   }
}