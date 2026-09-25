# Constitución del proyecto

1. **Stack simple:** usar solo Python y su biblioteca estándar; toda dependencia externa requiere justificación en la spec.
2. **Spec antes que código:** cada funcionalidad debe estar descrita en `docs/spec.md` antes de implementarse; código y spec deben coincidir.
3. **Lógica separada:** la lógica de hábitos y rachas no puede importar ni depender de la interfaz de usuario.
4. **Tests obligatorios:** toda regla de negocio y corrección de errores debe incluir tests automatizados con `unittest`.
5. **Persistencia segura:** los datos se guardarán localmente en JSON, con escritura atómica y validación al cargarlos.
6. **Idioma consistente:** código, nombres y comentarios en inglés; mensajes visibles y documentación para el usuario en español.
