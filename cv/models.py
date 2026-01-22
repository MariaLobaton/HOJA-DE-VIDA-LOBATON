from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import Q, F


# ✅ VALIDADORES REUSABLES
telefono_validator = RegexValidator(
    regex=r"^\d{8,10}$",
    message="El teléfono debe tener solo números y entre 8 a 10 dígitos."
)

cedula_validator = RegexValidator(
    regex=r"^\d{10}$",
    message="La cédula debe tener exactamente 10 dígitos numéricos."
)


# ===============================
# ✅ DATOS PERSONALES
# ===============================
class DatosPersonales(models.Model):
    idperfil = models.AutoField(primary_key=True)
    descripcionperfil = models.CharField(max_length=50)
    perfilactivo = models.IntegerField(default=1)

    apellidos = models.CharField(max_length=60)
    nombres = models.CharField(max_length=60)
    nacionalidad = models.CharField(max_length=20)
    lugarnacimiento = models.CharField(max_length=60)
    fechanacimiento = models.DateField(null=True, blank=True)

    numerocedula = models.CharField(
        max_length=10,
        unique=True,
        validators=[cedula_validator]
    )

    sexo = models.CharField(max_length=1)
    estadocivil = models.CharField(max_length=50)
    licenciaconducir = models.CharField(max_length=6, blank=True, null=True)

    telefonoconvencional = models.CharField(
        max_length=10,
        blank=True, null=True,
        validators=[telefono_validator]
    )
    telefonofijo = models.CharField(
        max_length=10,
        blank=True, null=True,
        validators=[telefono_validator]
    )

    direcciontrabajo = models.CharField(max_length=50, blank=True, null=True)
    direcciondomiciliaria = models.CharField(max_length=50, blank=True, null=True)
    sitioweb = models.CharField(max_length=60, blank=True, null=True)

    def clean(self):
        # ✅ Validación fecha de nacimiento
        if self.fechanacimiento and self.fechanacimiento > timezone.now().date():
            raise ValidationError({"fechanacimiento": "La fecha de nacimiento no puede ser futura."})

    class Meta:
        db_table = "datospersonales"


# ===============================
# ✅ EXPERIENCIA LABORAL
# ===============================
class ExperienciaLaboral(models.Model):
    idexperiencialaboral = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    cargodesempenado = models.CharField(max_length=100)
    nombrempresa = models.CharField(max_length=50)
    lugarempresa = models.CharField(max_length=50)
    emailempresa = models.CharField(max_length=100)
    sitiowebempresa = models.CharField(max_length=100, blank=True, null=True)

    nombrecontactoempresarial = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoempresarial = models.CharField(
        max_length=10,
        blank=True, null=True,
        validators=[telefono_validator]
    )

    fechainiciogestion = models.DateField()
    fechafingestion = models.DateField(blank=True, null=True)

    descripcionfunciones = models.CharField(max_length=100)
    activarparaqueseveaenfront = models.BooleanField(default=True)

    rutacertificado = models.FileField(
        upload_to="certificados/experiencia/",
        blank=True,
        null=True
    )

    def clean(self):
        # ✅ Si hay fecha fin, debe ser mayor o igual a inicio
        if self.fechafingestion and self.fechafingestion < self.fechainiciogestion:
            raise ValidationError({
                "fechafingestion": "La fecha fin NO puede ser menor que la fecha de inicio."
            })

        # ✅ Evitar fechas futuras
        hoy = timezone.now().date()
        if self.fechainiciogestion > hoy:
            raise ValidationError({"fechainiciogestion": "La fecha de inicio no puede ser futura."})
        if self.fechafingestion and self.fechafingestion > hoy:
            raise ValidationError({"fechafingestion": "La fecha de fin no puede ser futura."})

    class Meta:
        db_table = "experiencialaboral"
        constraints = [
            models.CheckConstraint(
                # ✅ AQUÍ VA condition= (NO check=)
                condition=Q(fechafingestion__isnull=True) | Q(fechafingestion__gte=F("fechainiciogestion")),
                name="experiencia_fechas_validas"
            )
        ]


# ===============================
# ✅ RECONOCIMIENTOS
# ===============================
class Reconocimientos(models.Model):
    idreconocimiento = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    tiporeconocimiento = models.CharField(max_length=100)
    fechareconocimiento = models.DateField()
    descripcionreconocimiento = models.CharField(max_length=100)

    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(
        max_length=10,
        blank=True, null=True,
        validators=[telefono_validator]
    )

    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = models.FileField(upload_to="certificados/reconocimientos/", blank=True, null=True)

    def clean(self):
        hoy = timezone.now().date()
        if self.fechareconocimiento > hoy:
            raise ValidationError({"fechareconocimiento": "La fecha del reconocimiento no puede ser futura."})

    class Meta:
        db_table = "reconocimientos"


# ===============================
# ✅ CURSOS REALIZADOS
# ===============================
class CursosRealizados(models.Model):
    idcursorealizado = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    nombrecurso = models.CharField(max_length=100)
    fechainicio = models.DateField()
    fechafin = models.DateField()

    # ✅ NO permite negativos
    totalhoras = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    descripcioncurso = models.CharField(max_length=100)

    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(
        max_length=10,
        blank=True, null=True,
        validators=[telefono_validator]
    )

    emailempresapatrocinadora = models.CharField(max_length=60, blank=True, null=True)

    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = models.FileField(upload_to="certificados/cursos/", blank=True, null=True)

    def clean(self):
        if self.fechafin < self.fechainicio:
            raise ValidationError({"fechafin": "La fecha de fin NO puede ser menor que la fecha de inicio."})

        hoy = timezone.now().date()
        if self.fechainicio > hoy:
            raise ValidationError({"fechainicio": "La fecha de inicio no puede ser futura."})
        if self.fechafin > hoy:
            raise ValidationError({"fechafin": "La fecha de fin no puede ser futura."})

    class Meta:
        db_table = "cursosrealizados"
        constraints = [
            models.CheckConstraint(
                condition=Q(totalhoras__gte=0),
                name="curso_totalhoras_gte_0"
            ),
            models.CheckConstraint(
                condition=Q(fechafin__gte=F("fechainicio")),
                name="curso_fechas_validas"
            )
        ]


# ===============================
# ✅ PRODUCTOS ACADEMICOS
# ===============================
class ProductosAcademicos(models.Model):
    idproductoacademico = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    nombrerecurso = models.CharField(max_length=100)
    clasificador = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=100)

    activarparaqueseveaenfront = models.BooleanField(default=True)

    class Meta:
        db_table = "productosacademicos"


# ===============================
# ✅ PRODUCTOS LABORALES
# ===============================
class ProductosLaborales(models.Model):
    idproductoslaborales = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    nombreproducto = models.CharField(max_length=100)
    fechaproducto = models.DateField()
    descripcion = models.CharField(max_length=100)

    activarparaqueseveaenfront = models.BooleanField(default=True)

    def clean(self):
        hoy = timezone.now().date()
        if self.fechaproducto > hoy:
            raise ValidationError({"fechaproducto": "La fecha del producto no puede ser futura."})

    class Meta:
        db_table = "productoslaborales"


# ===============================
# ✅ VENTA GARAGE
# ===============================
class VentaGarage(models.Model):
    idventagarage = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    nombreproducto = models.CharField(max_length=100)
    estadoproducto = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=100)

    # ✅ NO permite negativos
    valordelbien = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    activarparaqueseveaenfront = models.BooleanField(default=True)

    class Meta:
        db_table = "ventagarage"
        constraints = [
            models.CheckConstraint(
                condition=Q(valordelbien__gte=0),
                name="garage_valor_gte_0"
            )
        ]
