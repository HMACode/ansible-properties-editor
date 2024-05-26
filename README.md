# ansible-properties-editor

+ Ansible module to edit java properties files

+ Two possible actions: 
  + update: updates the value for a given key if already exists, else appends the new property to the file
  + delete: comments the line where the key is declared 

+ Sample usage: 

````yml
---
- name: Sample play
  hosts: localhost
  tasks:
    - name: Test my custom module
      properties_editor:
        filepath: "/data/test.properties"
        properties:          
          - key: "user.email"
            action: "update"
            value: "test@test.com"
          
          - key: "user.password"
            action: delete
          
````